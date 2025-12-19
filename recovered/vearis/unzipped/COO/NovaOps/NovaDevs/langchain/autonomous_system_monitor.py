#!/usr/bin/env python3
# Autonomous System Monitor
# Created by Cosmos, Head of NovaOps
# April 4, 2025, 5:38 PM MST

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("autonomous_monitor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("AutonomousMonitor")

class AutonomousSystemMonitor:
    """Autonomous System Monitor for real-time monitoring and response."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize autonomous system monitor."""
        self.config = config
        self.redis_connection = None
        self.system_status = {}
        self.alert_history = []
        self.action_history = []
        self.check_interval = config.get("check_interval", 30)  # seconds
        self.report_interval = config.get("report_interval", 300)  # seconds
        self.last_report_time = 0
        self.running = True
        self.logger = logging.getLogger("AutonomousSystemMonitor")
        self.logger.info("Initializing autonomous system monitor")
    
    async def initialize(self):
        """Initialize autonomous system monitor."""
        try:
            # Initialize Redis connection if available
            try:
                import redis
                from redis.cluster import RedisCluster
                
                redis_config = self.config.get("redis", {})
                if redis_config.get("cluster_mode", False):
                    self.redis_connection = RedisCluster(
                        host=redis_config.get("host", "localhost"),
                        port=redis_config.get("port", 6379),
                        password=redis_config.get("password", None),
                        decode_responses=True
                    )
                else:
                    self.redis_connection = redis.Redis(
                        host=redis_config.get("host", "localhost"),
                        port=redis_config.get("port", 6379),
                        password=redis_config.get("password", None),
                        decode_responses=True
                    )
                
                self.logger.info("Redis connection established")
            except ImportError:
                self.logger.warning("Redis module not available, continuing without Redis connection")
            
            # Initialize system status
            self.system_status = {
                "nova_activation": {"status": "unknown", "last_check": 0},
                "framework_bridge": {"status": "unknown", "last_check": 0},
                "monitoring_systems": {"status": "unknown", "last_check": 0},
                "redis_streams": {"status": "unknown", "last_check": 0},
                "system_resources": {"status": "unknown", "last_check": 0}
            }
            
            # Start monitoring tasks
            asyncio.create_task(self._monitor_loop())
            asyncio.create_task(self._report_loop())
            
            self.logger.info("Autonomous system monitor initialized")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize autonomous system monitor: {e}")
            return False
    
    async def _monitor_loop(self):
        """Main monitoring loop."""
        try:
            while self.running:
                # Check all systems
                await self._check_nova_activation()
                await self._check_framework_bridge()
                await self._check_monitoring_systems()
                await self._check_redis_streams()
                await self._check_system_resources()
                
                # Process alerts
                await self._process_alerts()
                
                # Wait for next check
                await asyncio.sleep(self.check_interval)
        except Exception as e:
            self.logger.error(f"Error in monitoring loop: {e}")
    
    async def _report_loop(self):
        """Reporting loop."""
        try:
            while self.running:
                current_time = time.time()
                
                # Check if it's time to generate a report
                if current_time - self.last_report_time >= self.report_interval:
                    await self._generate_status_report()
                    self.last_report_time = current_time
                
                # Wait for a bit
                await asyncio.sleep(10)
        except Exception as e:
            self.logger.error(f"Error in reporting loop: {e}")
    
    async def _check_nova_activation(self):
        """Check Nova activation status."""
        try:
            # Check Nova activation files
            nova_files = [f for f in os.listdir() if f.startswith("nova_activation_nova-")]
            batch_files = [f for f in os.listdir() if f.startswith("batch_activation_")]
            
            if not nova_files and not batch_files:
                self.system_status["nova_activation"] = {
                    "status": "unknown",
                    "message": "No Nova activation files found",
                    "last_check": time.time()
                }
                return
            
            # Count Nova activation files
            nova_count = len(nova_files)
            
            # Get latest batch activation file
            if batch_files:
                batch_files.sort(reverse=True)
                latest_batch_file = batch_files[0]
                
                try:
                    with open(latest_batch_file, "r") as f:
                        batch_data = json.load(f)
                        
                    total_novas = len(batch_data.get("nova_ids", []))
                    successes = batch_data.get("successes", 0)
                    failures = batch_data.get("failures", 0)
                    
                    status = "healthy" if failures == 0 else "warning" if failures <= 5 else "critical"
                    
                    self.system_status["nova_activation"] = {
                        "status": status,
                        "message": f"Nova activation: {successes} successes, {failures} failures out of {total_novas} total",
                        "details": {
                            "total_novas": total_novas,
                            "successes": successes,
                            "failures": failures,
                            "latest_batch_file": latest_batch_file
                        },
                        "last_check": time.time()
                    }
                except Exception as e:
                    self.system_status["nova_activation"] = {
                        "status": "warning",
                        "message": f"Error parsing batch activation file: {e}",
                        "details": {
                            "nova_count": nova_count,
                            "latest_batch_file": latest_batch_file
                        },
                        "last_check": time.time()
                    }
            else:
                # No batch files, just count Nova files
                self.system_status["nova_activation"] = {
                    "status": "warning",
                    "message": f"Found {nova_count} Nova activation files, but no batch files",
                    "details": {
                        "nova_count": nova_count
                    },
                    "last_check": time.time()
                }
        except Exception as e:
            self.logger.error(f"Error checking Nova activation: {e}")
            self.system_status["nova_activation"] = {
                "status": "error",
                "message": f"Error checking Nova activation: {e}",
                "last_check": time.time()
            }
    
    async def _check_framework_bridge(self):
        """Check Framework Bridge status."""
        try:
            # Check Framework Bridge files
            bridge_files = [
                "framework_bridge_direct_implementation.py",
                "document_knowledge_handler.py",
                "knowledge_fusion_system.py",
                "neo4j_handler.py",
                "cross_framework_testing.py"
            ]
            
            missing_files = [f for f in bridge_files if not os.path.exists(f)]
            
            if missing_files:
                self.system_status["framework_bridge"] = {
                    "status": "warning",
                    "message": f"Missing Framework Bridge files: {', '.join(missing_files)}",
                    "details": {
                        "missing_files": missing_files,
                        "existing_files": [f for f in bridge_files if os.path.exists(f)]
                    },
                    "last_check": time.time()
                }
            else:
                # Check if processes are running
                try:
                    result = subprocess.run(
                        ["ps", "aux"],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    
                    output = result.stdout
                    
                    # Check for Framework Bridge processes
                    bridge_processes = [line for line in output.split("\n") if "framework_bridge" in line and "grep" not in line]
                    
                    if bridge_processes:
                        self.system_status["framework_bridge"] = {
                            "status": "healthy",
                            "message": f"Framework Bridge is running with {len(bridge_processes)} processes",
                            "details": {
                                "processes": bridge_processes
                            },
                            "last_check": time.time()
                        }
                    else:
                        self.system_status["framework_bridge"] = {
                            "status": "warning",
                            "message": "Framework Bridge files exist but no processes found",
                            "details": {
                                "files": bridge_files
                            },
                            "last_check": time.time()
                        }
                except Exception as e:
                    self.system_status["framework_bridge"] = {
                        "status": "warning",
                        "message": f"Error checking Framework Bridge processes: {e}",
                        "details": {
                            "files": bridge_files
                        },
                        "last_check": time.time()
                    }
        except Exception as e:
            self.logger.error(f"Error checking Framework Bridge: {e}")
            self.system_status["framework_bridge"] = {
                "status": "error",
                "message": f"Error checking Framework Bridge: {e}",
                "last_check": time.time()
            }
    
    async def _check_monitoring_systems(self):
        """Check monitoring systems status."""
        try:
            # Check monitoring script files
            monitoring_files = [
                "monitor_langchain_streams.sh",
                "monitor_streams.py",
                "monitor_framework_bridge_implementation.sh",
                "monitor_turbo_mode_streams.sh"
            ]
            
            missing_files = [f for f in monitoring_files if not os.path.exists(f)]
            
            # Check if monitoring processes are running
            try:
                result = subprocess.run(
                    ["ps", "aux"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                output = result.stdout
                
                # Check for monitoring processes
                monitoring_processes = [
                    line for line in output.split("\n") 
                    if any(mf in line for mf in monitoring_files) and "grep" not in line
                ]
                
                if missing_files:
                    self.system_status["monitoring_systems"] = {
                        "status": "warning",
                        "message": f"Missing monitoring files: {', '.join(missing_files)}",
                        "details": {
                            "missing_files": missing_files,
                            "existing_files": [f for f in monitoring_files if os.path.exists(f)],
                            "running_processes": monitoring_processes
                        },
                        "last_check": time.time()
                    }
                elif not monitoring_processes:
                    self.system_status["monitoring_systems"] = {
                        "status": "warning",
                        "message": "Monitoring files exist but no processes found",
                        "details": {
                            "files": [f for f in monitoring_files if os.path.exists(f)]
                        },
                        "last_check": time.time()
                    }
                else:
                    self.system_status["monitoring_systems"] = {
                        "status": "healthy",
                        "message": f"Monitoring systems are running with {len(monitoring_processes)} processes",
                        "details": {
                            "processes": monitoring_processes
                        },
                        "last_check": time.time()
                    }
            except Exception as e:
                self.system_status["monitoring_systems"] = {
                    "status": "warning",
                    "message": f"Error checking monitoring processes: {e}",
                    "details": {
                        "files": [f for f in monitoring_files if os.path.exists(f)]
                    },
                    "last_check": time.time()
                }
        except Exception as e:
            self.logger.error(f"Error checking monitoring systems: {e}")
            self.system_status["monitoring_systems"] = {
                "status": "error",
                "message": f"Error checking monitoring systems: {e}",
                "last_check": time.time()
            }
    
    async def _check_redis_streams(self):
        """Check Redis streams status."""
        try:
            if not self.redis_connection:
                self.system_status["redis_streams"] = {
                    "status": "unknown",
                    "message": "Redis connection not available",
                    "last_check": time.time()
                }
                return
            
            # Check key Redis streams
            streams = [
                "swarm:tasks:dispatch",
                "swarm:tasks:ack",
                "swarm:tasks:fail",
                "swarm:heartbeat:novaops",
                "swarm:status:core",
                "keystone:signal:in",
                "keystone:meta:telemetry"
            ]
            
            stream_status = {}
            
            for stream in streams:
                try:
                    # Check if stream exists
                    stream_info = self.redis_connection.xinfo_stream(stream)
                    
                    # Get stream length
                    length = stream_info.get("length", 0)
                    
                    # Get last entry time
                    last_entry_time = stream_info.get("last-entry-id", "0-0").split("-")[0]
                    last_entry_timestamp = int(last_entry_time) / 1000 if last_entry_time != "0" else 0
                    
                    # Calculate time since last entry
                    time_since_last_entry = time.time() - last_entry_timestamp if last_entry_timestamp > 0 else float("inf")
                    
                    # Determine status based on time since last entry
                    status = "healthy"
                    if time_since_last_entry > 3600:  # 1 hour
                        status = "warning"
                    elif time_since_last_entry > 86400:  # 1 day
                        status = "critical"
                    
                    stream_status[stream] = {
                        "status": status,
                        "length": length,
                        "last_entry_time": last_entry_timestamp,
                        "time_since_last_entry": time_since_last_entry
                    }
                except Exception as e:
                    stream_status[stream] = {
                        "status": "error",
                        "message": str(e)
                    }
            
            # Determine overall status
            if any(s.get("status") == "critical" for s in stream_status.values()):
                overall_status = "critical"
            elif any(s.get("status") == "warning" for s in stream_status.values()):
                overall_status = "warning"
            elif any(s.get("status") == "error" for s in stream_status.values()):
                overall_status = "error"
            else:
                overall_status = "healthy"
            
            self.system_status["redis_streams"] = {
                "status": overall_status,
                "message": f"Redis streams status: {overall_status}",
                "details": stream_status,
                "last_check": time.time()
            }
        except Exception as e:
            self.logger.error(f"Error checking Redis streams: {e}")
            self.system_status["redis_streams"] = {
                "status": "error",
                "message": f"Error checking Redis streams: {e}",
                "last_check": time.time()
            }
    
    async def _check_system_resources(self):
        """Check system resources."""
        try:
            # Check CPU usage
            try:
                cpu_result = subprocess.run(
                    ["top", "-bn1"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                cpu_output = cpu_result.stdout
                
                # Parse CPU usage
                cpu_line = next((line for line in cpu_output.split("\n") if "Cpu(s)" in line), "")
                cpu_usage = float(cpu_line.split(",")[0].split(":")[1].strip().replace("%id", "").strip()) if cpu_line else 0
                cpu_usage = 100 - cpu_usage  # Convert idle percentage to usage percentage
            except Exception as e:
                cpu_usage = None
                self.logger.error(f"Error checking CPU usage: {e}")
            
            # Check memory usage
            try:
                mem_result = subprocess.run(
                    ["free", "-m"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                mem_output = mem_result.stdout
                
                # Parse memory usage
                mem_lines = mem_output.split("\n")
                mem_line = next((line for line in mem_lines if line.startswith("Mem:")), "")
                
                if mem_line:
                    mem_parts = mem_line.split()
                    total_mem = int(mem_parts[1])
                    used_mem = int(mem_parts[2])
                    mem_usage_percent = (used_mem / total_mem) * 100 if total_mem > 0 else 0
                else:
                    total_mem = 0
                    used_mem = 0
                    mem_usage_percent = 0
            except Exception as e:
                total_mem = None
                used_mem = None
                mem_usage_percent = None
                self.logger.error(f"Error checking memory usage: {e}")
            
            # Check disk usage
            try:
                disk_result = subprocess.run(
                    ["df", "-h", "."],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                disk_output = disk_result.stdout
                
                # Parse disk usage
                disk_lines = disk_output.split("\n")
                disk_line = disk_lines[1] if len(disk_lines) > 1 else ""
                
                if disk_line:
                    disk_parts = disk_line.split()
                    disk_usage_percent = int(disk_parts[4].replace("%", ""))
                else:
                    disk_usage_percent = 0
            except Exception as e:
                disk_usage_percent = None
                self.logger.error(f"Error checking disk usage: {e}")
            
            # Determine overall status
            status = "healthy"
            message = "System resources are healthy"
            
            if cpu_usage is not None and cpu_usage > 90:
                status = "critical"
                message = f"CPU usage is critical: {cpu_usage:.1f}%"
            elif cpu_usage is not None and cpu_usage > 80:
                status = "warning"
                message = f"CPU usage is high: {cpu_usage:.1f}%"
            
            if mem_usage_percent is not None and mem_usage_percent > 90:
                status = "critical"
                message = f"Memory usage is critical: {mem_usage_percent:.1f}%"
            elif mem_usage_percent is not None and mem_usage_percent > 80 and status != "critical":
                status = "warning"
                message = f"Memory usage is high: {mem_usage_percent:.1f}%"
            
            if disk_usage_percent is not None and disk_usage_percent > 90:
                status = "critical"
                message = f"Disk usage is critical: {disk_usage_percent}%"
            elif disk_usage_percent is not None and disk_usage_percent > 80 and status != "critical":
                status = "warning"
                message = f"Disk usage is high: {disk_usage_percent}%"
            
            self.system_status["system_resources"] = {
                "status": status,
                "message": message,
                "details": {
                    "cpu_usage": cpu_usage,
                    "memory_usage": {
                        "total_mb": total_mem,
                        "used_mb": used_mem,
                        "usage_percent": mem_usage_percent
                    },
                    "disk_usage_percent": disk_usage_percent
                },
                "last_check": time.time()
            }
        except Exception as e:
            self.logger.error(f"Error checking system resources: {e}")
            self.system_status["system_resources"] = {
                "status": "error",
                "message": f"Error checking system resources: {e}",
                "last_check": time.time()
            }
    
    async def _process_alerts(self):
        """Process alerts based on system status."""
        try:
            # Check for critical or error status
            critical_systems = []
            warning_systems = []
            
            for system, status in self.system_status.items():
                if status.get("status") == "critical" or status.get("status") == "error":
                    critical_systems.append((system, status))
                elif status.get("status") == "warning":
                    warning_systems.append((system, status))
            
            # Handle critical alerts
            for system, status in critical_systems:
                alert = {
                    "system": system,
                    "status": status.get("status"),
                    "message": status.get("message"),
                    "timestamp": time.time()
                }
                
                # Add to alert history
                self.alert_history.append(alert)
                
                # Log alert
                self.logger.critical(f"ALERT: {system} - {status.get('message')}")
                
                # Send alert to Redis if available
                if self.redis_connection:
                    try:
                        self.redis_connection.xadd(
                            "system:alerts",
                            {
                                "type": "critical_alert",
                                "system": system,
                                "message": status.get("message"),
                                "details": json.dumps(status.get("details", {})),
                                "timestamp": str(time.time())
                            }
                        )
                    except Exception as e:
                        self.logger.error(f"Error sending alert to Redis: {e}")
                
                # Take action based on system
                await self._take_action(system, status)
            
            # Handle warning alerts
            for system, status in warning_systems:
                alert = {
                    "system": system,
                    "status": status.get("status"),
                    "message": status.get("message"),
                    "timestamp": time.time()
                }
                
                # Add to alert history
                self.alert_history.append(alert)
                
                # Log alert
                self.logger.warning(f"WARNING: {system} - {status.get('message')}")
                
                # Send alert to Redis if available
                if self.redis_connection:
                    try:
                        self.redis_connection.xadd(
                            "system:alerts",
                            {
                                "type": "warning_alert",
                                "system": system,
                                "message": status.get("message"),
                                "details": json.dumps(status.get("details", {})),
                                "timestamp": str(time.time())
                            }
                        )
                    except Exception as e:
                        self.logger.error(f"Error sending alert to Redis: {e}")
        except Exception as e:
            self.logger.error(f"Error processing alerts: {e}")
    
    async def _take_action(self, system: str, status: Dict[str, Any]):
        """Take action based on system status."""
        try:
            action = {
                "system": system,
                "status": status.get("status"),
                "message": status.get("message"),
                "action": "none",
                "result": "none",
                "timestamp": time.time()
            }
            
            # Take action based on system
            if system == "nova_activation" and status.get("status") in ["critical", "error"]:
                # Try to restart Nova activation
                self.logger.info(f"Taking action for {system}: Attempting to restart Nova activation")
                
                action["action"] = "restart_nova_activation"
                
                # Check if enhanced retry script exists
                if os.path.exists("docs/code_red/enhanced_retry_activations.py"):
                    try:
                        # Run enhanced retry script
                        result = subprocess.run(
                            ["python3", "docs/code_red/enhanced_retry_activations.py"],
                            capture_output=True,
                            text=True,
                            check=True
                        )
                        
                        action["result"] = "success"
                        action["details"] = {
                            "stdout": result.stdout,
                            "stderr": result.stderr
                        }
                        
                        self.logger.info(f"Successfully restarted Nova activation: {result.stdout}")
                    except Exception as e:
                        action["result"] = "failure"
                        action["details"] = {
                            "error": str(e)
                        }
                        
                        self.logger.error(f"Failed to restart Nova activation: {e}")
                else:
                    action["result"] = "failure"
                    action["details"] = {
                        "error": "Enhanced retry script not found"
                    }
                    
                    self.logger.error("Failed to restart Nova activation: Enhanced retry script not found")
            elif system == "monitoring_systems" and status.get("status") in ["critical", "error"]:
                # Try to restart monitoring systems
                self.logger.info(f"Taking action for {system}: Attempting to restart monitoring systems")
                
                action["action"] = "restart_monitoring_systems"
                
                # Check monitoring script files
                monitoring_files = [
                    "monitor_langchain_streams.sh",
                    "monitor_streams.py",
                    "monitor_framework_bridge_implementation.sh",
                    "monitor_turbo_mode_streams.sh"
                ]
                
                restart_results = {}
                
                for script in monitoring_files:
                    if os.path.exists(script):
                        try:
                            # Make script executable
                            os.chmod(script, 0o755)
                            
                            # Run script
                            if script.endswith(".sh"):
                                result = subprocess.run(
                                    ["bash", script],
                                    capture_output=True,
                                    text=True
                                )
                            elif script.endswith(".py"):
                                result = subprocess.run(
                                    ["python3", script],
                                    capture_output=True,
                                    text=True
                                )
                            else:
                                continue
                            
                            restart_results[script] = {
                                "success": result.returncode == 0,
                                "stdout": result.stdout,
                                "stderr": result.stderr
                            }
                            
                            if result.returncode == 0:
                                self.logger.info(f"Successfully restarted {script}")
                            else:
                                self.logger.error(f"Failed to restart {script}: {result.stderr}")
                        except Exception as e:
                            restart_results[script] = {
                                "success": False,
                                "error": str(e)
                            }
                            
                            self.logger.error(f"Failed to restart {script}: {e}")
                
                # Check if any restarts succeeded
                if any(r.get("success", False) for r in restart_results.values()):
                    action["result"] = "partial_success"
                else:
                    action["result"] = "failure"
                
                action["details"] = restart_results
            
            # Add action to history
            self.action_history.append(action)
            
            # Send action to Redis if available
            if self.redis_connection:
                try:
                    self.redis_connection.xadd(
                        "system:actions",
                        {
                            "type": "system_action",
                            "system": system,
                            "action": action["action"],
                            "result": action["result"],
                            "details": json.dumps(action.get("details", {})),
                            "timestamp": str(time.time())
                        }
                    )
                except Exception as e:
                    self.logger.error(f"Error sending action to Redis: {e}")
        except Exception as e:
            self.logger.error(f"Error taking action for {system}: {e}")
    
    async def _generate_status_report(self):
        """Generate status report."""
        try:
            # Create report
            report = {
                "timestamp": time.time(),
                "system_status": self.system_status,
                "alerts": self.alert_history[-10:] if self.alert_history else [],
                "actions": self.action_history[-10:] if self.action_history else [],
                "summary": {
                    "status": "healthy",
                    "message": "All systems operational"
                }
            }
            
            # Determine overall status
            if any(s.get("status") in ["critical", "error"] for s in self.system_status.values()):
                report["summary"]["status"] = "critical"
                report["summary"]["message"] = "Critical issues detected"
            elif any(s.get("status") == "warning" for s in self.system_status.values()):
                report["summary"]["status"] = "warning"
                report["summary"]["message"] = "Warnings detected"
            
            # Save report to file
            report_file = f"system_status_{int(time.time())}.json"
            with open(report_file, "w") as f:
                json.dump(report, f, indent=2)
            
            self.logger.info(f"Generated status report: {report_file}")
            
            # Send report to Redis if available
            if self.redis_connection:
                try:
                    self.redis_connection.xadd(
                        "system:reports",
                        {
                            "type": "status_report",
                            "summary_status": report["summary"]["status"],
                            "summary_message": report["summary"]["message"],
                            "report_file": report_file,
                            "timestamp": str(time.time())
                        }
                    )
                except Exception as e:
                    self.logger.error(f"Error sending report to Redis: {e}")
            
            # Generate human-readable report
            human_report = self._generate_human_readable_report(report)
            
            # Save human-readable report to file
            human_report_file = f"system_status_{int(time.time())}.md"
            with open(human_report_file, "w") as f:
                f.write(human_report)
            
            self.logger.info(f"Generated human-readable status report: {human_report_file}")
            
            return report
        except Exception as e:
            self.logger.error(f"Error generating status report: {e}")
            return None
    
