# app/services/task_queue.py
import asyncio
from typing import Dict, Any, Callable, Coroutine
import uuid
import logging

logger = logging.getLogger("hydrous")

class TaskQueue:
    """Gestor de tareas asíncronas con seguimiento de estado."""
    
    def __init__(self):
        self.tasks: Dict[str, Dict[str, Any]] = {}
        
    async def add_task(self, coroutine: Coroutine, task_name: str = None) -> str:
        """Añade una tarea a la cola y retorna su ID."""
        task_id = str(uuid.uuid4())
        task_name = task_name or f"task-{task_id[:8]}"
        
        self.tasks[task_id] = {
            "name": task_name,
            "status": "pending",
            "result": None,
            "error": None,
            "created_at": asyncio.get_event_loop().time()
        }
        
        # Crear y ejecutar la tarea
        task = asyncio.create_task(self._run_task(task_id, coroutine))
        asyncio.ensure_future(task)
        
        return task_id
        
    async def _run_task(self, task_id: str, coroutine: Coroutine):
        """Ejecuta la tarea y actualiza su estado."""
        try:
            # Marcar como en ejecución
            self.tasks[task_id]["status"] = "running"
            
            # Ejecutar la tarea
            result = await coroutine
            
            # Actualizar con resultado exitoso
            self.tasks[task_id]["status"] = "completed"
            self.tasks[task_id]["result"] = result
            
            return result
        except Exception as e:
            logger.error(f"Error en tarea {task_id}: {str(e)}", exc_info=True)
            
            # Actualizar con error
            self.tasks[task_id]["status"] = "failed"
            self.tasks[task_id]["error"] = str(e)
            
            return None
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Obtiene el estado actual de una tarea."""
        if task_id not in self.tasks:
            return {"status": "not_found"}
        
        return self.tasks[task_id]
    
    def clear_old_tasks(self, max_age_seconds: int = 3600):
        """Limpia tareas antiguas completadas o fallidas."""
        current_time = asyncio.get_event_loop().time()
        
        to_delete = []
        for task_id, task_info in self.tasks.items():
            if task_info["status"] in ["completed", "failed"]:
                task_age = current_time - task_info["created_at"]
                if task_age > max_age_seconds:
                    to_delete.append(task_id)
        
        for task_id in to_delete:
            del self.tasks[task_id]

# Instancia global
task_queue = TaskQueue()