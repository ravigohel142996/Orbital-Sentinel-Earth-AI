"""
==============================================================================
Orbital Sentinel - Storage Service
Lightweight JSON-based storage for risk logs and predictions
==============================================================================
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from loguru import logger

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.models import RiskPrediction, DashboardStats, RiskType, RiskLevel


class StorageService:
    """
    JSON file-based storage service for risk predictions and logs.
    Provides lightweight persistence without database dependencies.
    """
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize storage service.
        
        Args:
            data_dir: Directory for storing JSON files
        """
        self.data_dir = data_dir or Path(__file__).parent.parent / "data"
        self.predictions_file = self.data_dir / "predictions.json"
        self.stats_file = self.data_dir / "stats.json"
        
        # Ensure data directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize files if they don't exist
        self._init_files()
        
        logger.info(f"Storage service initialized at {self.data_dir}")
    
    def _init_files(self):
        """Initialize JSON files with empty data if they don't exist"""
        if not self.predictions_file.exists():
            self._write_json(self.predictions_file, {"predictions": []})
        
        if not self.stats_file.exists():
            initial_stats = {
                "total_predictions": 0,
                "active_risks": 0,
                "critical_risks": 0,
                "regions_monitored": 0,
                "last_update": datetime.utcnow().isoformat(),
                "risk_breakdown": {},
            }
            self._write_json(self.stats_file, initial_stats)
    
    def _read_json(self, file_path: Path) -> Dict[str, Any]:
        """Read JSON file safely"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"Error reading {file_path}: {e}")
            return {}
    
    def _write_json(self, file_path: Path, data: Dict[str, Any]):
        """Write JSON file safely"""
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error writing {file_path}: {e}")
    
    async def save_prediction(self, prediction: RiskPrediction) -> bool:
        """
        Save a risk prediction to storage.
        
        Args:
            prediction: RiskPrediction to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            data = self._read_json(self.predictions_file)
            predictions = data.get("predictions", [])
            
            # Convert prediction to dict
            pred_dict = prediction.model_dump()
            pred_dict["timestamp"] = prediction.timestamp.isoformat()
            pred_dict["location"] = prediction.location.model_dump()
            if prediction.raw_data:
                pred_dict["raw_data"]["timestamp"] = prediction.raw_data.timestamp.isoformat()
            
            # Add to list (keep last 1000 predictions)
            predictions.append(pred_dict)
            if len(predictions) > 1000:
                predictions = predictions[-1000:]
            
            data["predictions"] = predictions
            self._write_json(self.predictions_file, data)
            
            # Update stats
            await self._update_stats(prediction)
            
            logger.info(f"Saved prediction {prediction.risk_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save prediction: {e}")
            return False
    
    async def _update_stats(self, prediction: RiskPrediction):
        """Update dashboard statistics with new prediction"""
        try:
            stats = self._read_json(self.stats_file)
            
            stats["total_predictions"] = stats.get("total_predictions", 0) + 1
            stats["last_update"] = datetime.utcnow().isoformat()
            
            # Update risk breakdown
            risk_breakdown = stats.get("risk_breakdown", {})
            risk_type = prediction.risk_type.value
            risk_breakdown[risk_type] = risk_breakdown.get(risk_type, 0) + 1
            stats["risk_breakdown"] = risk_breakdown
            
            # Update active risks count (risks in last hour)
            data = self._read_json(self.predictions_file)
            predictions = data.get("predictions", [])
            one_hour_ago = datetime.utcnow().timestamp() - 3600
            
            active_risks = sum(
                1 for p in predictions
                if datetime.fromisoformat(p["timestamp"]).timestamp() > one_hour_ago
            )
            stats["active_risks"] = active_risks
            
            # Update critical risks count
            critical_risks = sum(
                1 for p in predictions
                if (datetime.fromisoformat(p["timestamp"]).timestamp() > one_hour_ago
                    and p["risk_level"] in ["critical", "high"])
            )
            stats["critical_risks"] = critical_risks
            
            # Count unique regions
            regions = set()
            for p in predictions[-100:]:  # Last 100 predictions
                loc = p.get("location", {})
                if loc.get("region"):
                    regions.add(loc["region"])
            stats["regions_monitored"] = len(regions) or 1
            
            self._write_json(self.stats_file, stats)
            
        except Exception as e:
            logger.error(f"Failed to update stats: {e}")
    
    async def get_predictions(
        self,
        limit: int = 50,
        risk_type: Optional[str] = None,
        risk_level: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get recent predictions with optional filtering.
        
        Args:
            limit: Maximum number of predictions to return
            risk_type: Filter by risk type
            risk_level: Filter by risk level
            
        Returns:
            List of prediction dictionaries
        """
        try:
            data = self._read_json(self.predictions_file)
            predictions = data.get("predictions", [])
            
            # Apply filters
            if risk_type:
                predictions = [p for p in predictions if p.get("risk_type") == risk_type]
            
            if risk_level:
                predictions = [p for p in predictions if p.get("risk_level") == risk_level]
            
            # Return most recent predictions
            return predictions[-limit:][::-1]  # Most recent first
            
        except Exception as e:
            logger.error(f"Failed to get predictions: {e}")
            return []
    
    async def get_stats(self) -> DashboardStats:
        """
        Get current dashboard statistics.
        
        Returns:
            DashboardStats object
        """
        try:
            stats = self._read_json(self.stats_file)
            return DashboardStats(
                total_predictions=stats.get("total_predictions", 0),
                active_risks=stats.get("active_risks", 0),
                critical_risks=stats.get("critical_risks", 0),
                regions_monitored=stats.get("regions_monitored", 0),
                last_update=datetime.fromisoformat(stats.get("last_update", datetime.utcnow().isoformat())),
                risk_breakdown=stats.get("risk_breakdown", {}),
            )
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return DashboardStats()
    
    async def clear_old_predictions(self, days: int = 7) -> int:
        """
        Remove predictions older than specified days.
        
        Args:
            days: Number of days to keep
            
        Returns:
            Number of predictions removed
        """
        try:
            data = self._read_json(self.predictions_file)
            predictions = data.get("predictions", [])
            
            cutoff = datetime.utcnow().timestamp() - (days * 24 * 3600)
            original_count = len(predictions)
            
            predictions = [
                p for p in predictions
                if datetime.fromisoformat(p["timestamp"]).timestamp() > cutoff
            ]
            
            data["predictions"] = predictions
            self._write_json(self.predictions_file, data)
            
            removed = original_count - len(predictions)
            logger.info(f"Cleared {removed} old predictions")
            return removed
            
        except Exception as e:
            logger.error(f"Failed to clear old predictions: {e}")
            return 0


# Singleton instance
_storage_service = None


def get_storage_service() -> StorageService:
    """Get or create the singleton storage service instance"""
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService()
    return _storage_service
