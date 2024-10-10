# Adding a Custom Scanner to the Shield Application

This guide will show you how to create and add a new custom scanner to the Shield application. These scanners extend the base scanner class for added functionality.

## Steps:

### 1. Create Your Scanner Class:
- Open a code editor.
- Write a new python class that extends from the abstract base scanner class (i.e. `BaseScanner.py`).

**Note**: Name your class file and class name identically, with the suffix `Scanner` (e.g., `MyCustomScanner.py` containing the class `MyCustomScanner`). This keeps things consistent with other scanner classes.

### 2. Place Your Class File:
- Save your Python class file (e.g., `MyCustomScanner.py`) inside the `scanners` folder within the `shield` service folder in the repository.

### 3. Configure Your Scanner:
- Navigate to the `conf` folder within the `shield` service folder.
- Open the `shield_scanner.properties` file.
- Add a new entry for your scanner. Refer to existing scanner entries in the file for guidance.

### 4. Build and deploy:
- Now build the paig-server module.
- Deploy the generate whl file using pip command.
- Restart/start the shield service.


## Additional Notes
- Remember to restart your application for the changes to take effect.
- If you encounter any issues, contact the development team for further assistance.

That's it! You've successfully added your new scanner, ready for use.
