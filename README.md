A containerized Command Line Application (CLA) built with Python 3.13. This tool manages tasks through the terminal using a secure, non-root Docker environment.

---

## Quick Start

### 1. Build the Docker Image
Execute the following command in the project directory:
docker build -t task-manager:1.0.0 .

### 2. Set up Data Permissions
On Linux systems, the data directory must be writable by the container's internal user:
mkdir -p data && chmod 777 data

### 3. Run the Application
Use the following command structure to interact with the manager:
docker run --rm -v $(pwd)/data:/data task-manager:1.0.0 [command]

---

## Usage Examples

| Action | Command |
| :--- | :--- |
| Add a Task | docker run --rm -v $(pwd)/data:/data task-manager:1.0.0 add "Task Name" |
| List Tasks | docker run --rm -v $(pwd)/data:/data task-manager:1.0.0 list |
| Mark Done  | docker run --rm -v $(pwd)/data:/data task-manager:1.0.0 done [ID] |
| View Stats | docker run --rm -v $(pwd)/data:/data task-manager:1.0.0 stats |
