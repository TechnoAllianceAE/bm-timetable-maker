"""
Timetable persistence and caching system.

This module provides efficient caching of generated timetables to reduce
regeneration overhead and enable resumption of optimization processes.
"""

import json
import os
import time
import hashlib
import tempfile
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@dataclass
class TimetableCacheEntry:
    """Represents a cached timetable entry."""
    timetable_id: str
    session_id: str
    generation: int
    fitness_score: float
    coverage: float
    created_at: str
    last_accessed: str
    file_path: str
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TimetableCacheEntry':
        """Create from dictionary loaded from JSON."""
        return cls(**data)


class TimetableCache:
    """
    Manages persistent caching of timetables during generation and optimization.
    
    Features:
    - Stores timetables in temporary files with metadata
    - Automatic cleanup based on age and completion status
    - Session-based organization
    - Generation tracking for GA evolution
    - Quick lookup by ID or fitness score
    """
    
    def __init__(self, 
                 cache_dir: Optional[str] = None,
                 max_age_hours: int = 24,
                 max_cache_size_mb: int = 500,
                 auto_cleanup: bool = True):
        """
        Initialize timetable cache.
        
        Args:
            cache_dir: Directory for cache files (default: temp directory)
            max_age_hours: Maximum age before auto-cleanup
            max_cache_size_mb: Maximum cache size before cleanup
            auto_cleanup: Enable automatic cleanup
        """
        self.max_age_hours = max_age_hours
        self.max_cache_size_mb = max_cache_size_mb
        self.auto_cleanup = auto_cleanup
        
        # Setup cache directory
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            self.cache_dir = Path(tempfile.gettempdir()) / "timetable_cache"
        
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Index file for quick lookups
        self.index_file = self.cache_dir / "cache_index.json"
        self.index: Dict[str, TimetableCacheEntry] = {}
        
        # Load existing index
        self._load_index()
        
        # Perform initial cleanup if enabled
        if self.auto_cleanup:
            self._cleanup_expired()
    
    def store_timetable(self, 
                       timetable: Dict[str, Any],
                       session_id: str,
                       generation: int = 0,
                       fitness_score: float = 0.0,
                       metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Store a timetable in the cache.
        
        Args:
            timetable: Timetable data to store
            session_id: Session identifier for grouping
            generation: GA generation number (0 for non-GA)
            fitness_score: Quality score of the timetable
            metadata: Additional metadata
            
        Returns:
            str: Unique timetable ID for later retrieval
        """
        # Generate unique ID
        timetable_id = self._generate_timetable_id(timetable, session_id, generation)
        
        # Extract coverage from timetable metadata
        coverage = timetable.get('metadata', {}).get('coverage', 1.0)
        
        # Create cache entry
        timestamp = datetime.now().isoformat()
        file_path = self.cache_dir / f"{timetable_id}.json"
        
        entry = TimetableCacheEntry(
            timetable_id=timetable_id,
            session_id=session_id,
            generation=generation,
            fitness_score=fitness_score,
            coverage=coverage,
            created_at=timestamp,
            last_accessed=timestamp,
            file_path=str(file_path),
            metadata=metadata or {}
        )
        
        try:
            # Store timetable data
            with open(file_path, 'w') as f:
                json.dump(timetable, f, indent=2, default=str)
            
            # Update index
            self.index[timetable_id] = entry
            self._save_index()
            
            logger.info(f"Stored timetable {timetable_id} (session: {session_id}, gen: {generation})")
            
            # Periodic cleanup
            if self.auto_cleanup and len(self.index) % 10 == 0:
                self._cleanup_expired()
            
            return timetable_id
            
        except Exception as e:
            logger.error(f"Failed to store timetable {timetable_id}: {e}")
            raise
    
    def retrieve_timetable(self, timetable_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a timetable from cache.
        
        Args:
            timetable_id: ID of the timetable to retrieve
            
        Returns:
            Timetable data if found, None otherwise
        """
        if timetable_id not in self.index:
            return None
        
        entry = self.index[timetable_id]
        
        try:
            # Load timetable data
            with open(entry.file_path, 'r') as f:
                timetable = json.load(f)
            
            # Update last accessed time
            entry.last_accessed = datetime.now().isoformat()
            self.index[timetable_id] = entry
            self._save_index()
            
            logger.debug(f"Retrieved timetable {timetable_id}")
            return timetable
            
        except Exception as e:
            logger.error(f"Failed to retrieve timetable {timetable_id}: {e}")
            # Remove corrupted entry
            self._remove_entry(timetable_id)
            return None
    
    def list_session_timetables(self, session_id: str) -> List[TimetableCacheEntry]:
        """
        List all timetables for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of cache entries for the session
        """
        return [entry for entry in self.index.values() 
                if entry.session_id == session_id]
    
    def get_best_timetable(self, session_id: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """
        Get the best timetable from a session based on fitness score.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Tuple of (timetable_id, timetable_data) if found
        """
        session_entries = self.list_session_timetables(session_id)
        
        if not session_entries:
            return None
        
        best_entry = max(session_entries, key=lambda e: e.fitness_score)
        timetable = self.retrieve_timetable(best_entry.timetable_id)
        
        if timetable:
            return best_entry.timetable_id, timetable
        
        return None
    
    def get_generation_population(self, session_id: str, generation: int) -> List[Dict[str, Any]]:
        """
        Get all timetables from a specific GA generation.
        
        Args:
            session_id: Session identifier  
            generation: Generation number
            
        Returns:
            List of timetables from that generation
        """
        entries = [entry for entry in self.index.values()
                  if entry.session_id == session_id and entry.generation == generation]
        
        timetables = []
        for entry in entries:
            timetable = self.retrieve_timetable(entry.timetable_id)
            if timetable:
                timetables.append(timetable)
        
        return timetables
    
    def store_ga_population(self, 
                           population: List[Dict[str, Any]], 
                           session_id: str, 
                           generation: int,
                           fitness_scores: List[float]) -> List[str]:
        """
        Store an entire GA population.
        
        Args:
            population: List of timetables
            session_id: Session identifier
            generation: Generation number
            fitness_scores: Corresponding fitness scores
            
        Returns:
            List of generated timetable IDs
        """
        timetable_ids = []
        
        for i, (timetable, fitness) in enumerate(zip(population, fitness_scores)):
            metadata = {
                'population_index': i,
                'population_size': len(population)
            }
            
            tt_id = self.store_timetable(
                timetable=timetable,
                session_id=session_id,
                generation=generation,
                fitness_score=fitness,
                metadata=metadata
            )
            timetable_ids.append(tt_id)
        
        logger.info(f"Stored GA population: {len(timetable_ids)} timetables "
                   f"(session: {session_id}, gen: {generation})")
        
        return timetable_ids
    
    def complete_session(self, session_id: str, keep_best: bool = True):
        """
        Mark a session as complete and optionally clean up intermediate results.
        
        Args:
            session_id: Session identifier
            keep_best: Whether to keep the best timetable
        """
        session_entries = self.list_session_timetables(session_id)
        
        if not session_entries:
            logger.warning(f"No timetables found for session {session_id}")
            return
        
        if keep_best:
            # Keep only the best timetable
            best_entry = max(session_entries, key=lambda e: e.fitness_score)
            
            # Mark as completed
            best_entry.metadata['session_completed'] = True
            best_entry.metadata['completion_time'] = datetime.now().isoformat()
            self.index[best_entry.timetable_id] = best_entry
            
            # Remove all others
            for entry in session_entries:
                if entry.timetable_id != best_entry.timetable_id:
                    self._remove_entry(entry.timetable_id)
            
            logger.info(f"Session {session_id} completed. Kept best timetable: {best_entry.timetable_id}")
        else:
            # Remove all timetables from session
            for entry in session_entries:
                self._remove_entry(entry.timetable_id)
            
            logger.info(f"Session {session_id} completed. All timetables removed.")
        
        self._save_index()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get statistics about the cache."""
        total_files = len(self.index)
        total_size = sum(os.path.getsize(entry.file_path) 
                        for entry in self.index.values() 
                        if os.path.exists(entry.file_path))
        
        # Group by session
        sessions = {}
        for entry in self.index.values():
            if entry.session_id not in sessions:
                sessions[entry.session_id] = {'count': 0, 'generations': set()}
            sessions[entry.session_id]['count'] += 1
            sessions[entry.session_id]['generations'].add(entry.generation)
        
        return {
            'total_timetables': total_files,
            'total_size_mb': total_size / (1024 * 1024),
            'cache_directory': str(self.cache_dir),
            'active_sessions': len(sessions),
            'session_details': {sid: {'count': info['count'], 
                                     'generations': len(info['generations'])}
                               for sid, info in sessions.items()}
        }
    
    def cleanup_all(self):
        """Remove all cached timetables."""
        for timetable_id in list(self.index.keys()):
            self._remove_entry(timetable_id)
        
        self.index.clear()
        self._save_index()
        
        logger.info("All cached timetables removed")
    
    # Private methods
    
    def _generate_timetable_id(self, timetable: Dict[str, Any], 
                              session_id: str, generation: int) -> str:
        """Generate a unique ID for a timetable."""
        # Create hash of timetable content
        content_str = json.dumps(timetable, sort_keys=True, default=str)
        content_hash = hashlib.md5(content_str.encode()).hexdigest()[:8]
        
        # Include timestamp to ensure uniqueness
        timestamp = int(time.time() * 1000) % 1000000  # Last 6 digits
        
        return f"{session_id}_{generation:03d}_{content_hash}_{timestamp}"
    
    def _load_index(self):
        """Load the cache index from disk."""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r') as f:
                    data = json.load(f)
                    self.index = {
                        tid: TimetableCacheEntry.from_dict(entry_data)
                        for tid, entry_data in data.items()
                    }
                logger.debug(f"Loaded cache index with {len(self.index)} entries")
            except Exception as e:
                logger.error(f"Failed to load cache index: {e}")
                self.index = {}
    
    def _save_index(self):
        """Save the cache index to disk."""
        try:
            data = {tid: entry.to_dict() for tid, entry in self.index.items()}
            with open(self.index_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save cache index: {e}")
    
    def _remove_entry(self, timetable_id: str):
        """Remove a cache entry and its file."""
        if timetable_id not in self.index:
            return
        
        entry = self.index[timetable_id]
        
        # Remove file
        try:
            if os.path.exists(entry.file_path):
                os.remove(entry.file_path)
        except Exception as e:
            logger.error(f"Failed to remove file {entry.file_path}: {e}")
        
        # Remove from index
        del self.index[timetable_id]
    
    def _cleanup_expired(self):
        """Remove expired cache entries."""
        cutoff_time = datetime.now() - timedelta(hours=self.max_age_hours)
        cutoff_str = cutoff_time.isoformat()
        
        expired_ids = []
        for timetable_id, entry in self.index.items():
            # Skip completed sessions (they should be kept longer)
            if entry.metadata.get('session_completed', False):
                continue
            
            if entry.created_at < cutoff_str:
                expired_ids.append(timetable_id)
        
        for timetable_id in expired_ids:
            self._remove_entry(timetable_id)
        
        if expired_ids:
            logger.info(f"Cleaned up {len(expired_ids)} expired timetable(s)")
            self._save_index()
        
        # Also check total cache size
        self._cleanup_oversized()
    
    def _cleanup_oversized(self):
        """Remove oldest entries if cache is too large."""
        total_size = sum(os.path.getsize(entry.file_path) 
                        for entry in self.index.values() 
                        if os.path.exists(entry.file_path))
        
        max_size_bytes = self.max_cache_size_mb * 1024 * 1024
        
        if total_size <= max_size_bytes:
            return
        
        # Sort by last accessed time (oldest first)
        entries_by_age = sorted(
            [(tid, entry) for tid, entry in self.index.items()
             if not entry.metadata.get('session_completed', False)],
            key=lambda x: x[1].last_accessed
        )
        
        removed_count = 0
        for timetable_id, entry in entries_by_age:
            self._remove_entry(timetable_id)
            removed_count += 1
            
            # Check size again
            total_size = sum(os.path.getsize(e.file_path) 
                            for e in self.index.values() 
                            if os.path.exists(e.file_path))
            
            if total_size <= max_size_bytes:
                break
        
        if removed_count > 0:
            logger.info(f"Cleaned up {removed_count} timetables due to size limit")
            self._save_index()