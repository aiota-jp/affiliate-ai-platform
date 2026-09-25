import logging
logger=logging.getLogger("affiliate-agent-harness")
def log_event(level: str,run_key: str,step: str,message: str)->None:
    getattr(logger,level.lower(),logger.info)(f"run_key={run_key} step={step} message={message}")
