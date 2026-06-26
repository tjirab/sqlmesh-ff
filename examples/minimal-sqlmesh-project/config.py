import os
from sqlmesh import Model

def get_models() -> list[Model]:
    """
    Python bootstrap file to load and configure all SQLMesh models 
    for the project. Models are dynamically loaded from the 'models' subdirectory.
    """
    print("Loading SQLMesh models...")
    
    # Dynamically import the required function from the module
    from .models.core_model import core_model

    return [
        core_model(),
        # Add other models here: e.g., secondary_metrics_model(), etc.
    ]

if __name__ == "__main__":
    print("Bootstrap executed successfully.")
