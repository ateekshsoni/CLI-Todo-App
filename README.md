# Professional Todo CLI Application

A fully functional, professional-quality command-line todo application built with Python. This project demonstrates industry best practices, clean code architecture, and modern Python development techniques.

## 🌟 Features

- **Full CRUD Operations**: Create, Read, Update, Delete tasks
- **Priority Management**: High, Medium, Low priority levels
- **Status Tracking**: Pending, In Progress, Completed statuses
- **Data Persistence**: JSON-based storage in user's home directory
- **Beautiful CLI**: Rich terminal output with colors, tables, and panels
- **Input Validation**: Robust error handling and user input validation
- **Statistics**: Task completion rates and breakdowns
- **Filtering**: View tasks by status, priority, or show all
- **Bulk Operations**: Clear all completed tasks at once

## 📋 Requirements

- Python 3.8 or higher
- Virtual environment (recommended)

## 🚀 Installation & Setup

1. **Clone/Download the project**
   ```bash
   cd /path/to/Todo-Cli
   ```

2. **Activate your virtual environment**
   ```bash
   source ven/bin/activate  # On macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 📖 Usage Examples

### Basic Commands

```bash
# Add a simple task
python main.py add "Buy groceries"

# Add a task with description and priority
python main.py add "Complete project" --desc "Finish the todo CLI app" --priority high

# List active tasks (pending + in progress)
python main.py list

# List all tasks
python main.py list --all

# List only completed tasks
python main.py list --status completed

# Show detailed information about a task
python main.py show 1

# Update a task's title and priority
python main.py update 1 --title "Buy organic groceries" --priority high

# Mark a task as completed
python main.py complete 1

# Update task status to in-progress
python main.py update 1 --status in_progress

# Delete a task (with confirmation)
python main.py delete 1

# Force delete without confirmation
python main.py delete 1 --force

# Show task statistics
python main.py stats

# Clear all completed tasks
python main.py clear

# Get help for any command
python main.py --help
python main.py add --help
```

## 🏗️ Code Architecture

The application follows professional software development patterns:

### 1. **Layered Architecture**
- **Presentation Layer** (`TodoCLI`): Handles user interface and formatting
- **Business Logic Layer** (`TodoManager`): Core application logic and operations
- **Data Access Layer** (`TodoStorage`): Handles data persistence and retrieval

### 2. **Data Models**
- **Task Class**: Represents a single todo item with proper encapsulation
- **Enums**: Type-safe priority and status definitions
- **Serialization**: Clean JSON conversion methods

### 3. **Design Patterns Used**
- **Single Responsibility Principle**: Each class has one clear purpose
- **Dependency Injection**: Clean separation of concerns
- **Factory Pattern**: Task creation from dictionary data
- **Command Pattern**: CLI commands as discrete operations

### 4. **Error Handling**
- Comprehensive exception handling at all layers
- Graceful degradation when data files are corrupted
- User-friendly error messages with actionable guidance

## 📁 Data Storage

Tasks are stored in JSON format at:
```
~/.todo-cli/todos.json
```

The data structure includes:
- Unique task IDs
- Creation and completion timestamps
- All task metadata (title, description, priority, status)

## 🎨 Key Learning Points

### 1. **Modern Python Features**
- **Type Hints**: Full type annotation for better code clarity
- **Enums**: Type-safe constants for priorities and statuses
- **Dataclasses Alternative**: Manual class implementation with proper methods
- **Context Managers**: File handling with automatic cleanup
- **Pathlib**: Modern path handling instead of os.path

### 2. **CLI Best Practices**
- **Typer Framework**: Modern, type-hint-based CLI framework
- **Rich Output**: Beautiful terminal formatting with colors and tables
- **Command Structure**: Logical command organization
- **Help Documentation**: Comprehensive help text for all commands
- **Input Validation**: Proper argument and option validation

### 3. **Code Organization**
- **Modular Design**: Clear separation of concerns
- **Documentation**: Comprehensive docstrings and comments
- **Constants**: Configuration values in dedicated section
- **Import Organization**: Logical grouping of imports

### 4. **Professional Practices**
- **Error Handling**: Defensive programming with try-catch blocks
- **Logging**: Console output for user feedback
- **Data Validation**: Input sanitization and validation
- **User Experience**: Confirmation prompts for destructive operations

## 🔧 Extending the Application

The modular design makes it easy to add new features:

### Adding New Commands
1. Create a new function decorated with `@app.command()`
2. Use the existing `TodoManager` methods or add new ones
3. Follow the pattern of error handling and user feedback

### Adding New Data Fields
1. Extend the `Task` class with new attributes
2. Update `to_dict()` and `from_dict()` methods
3. Modify display methods in `TodoCLI` class

### Changing Storage Backend
1. Implement a new storage class following the `TodoStorage` interface
2. Replace the storage implementation in `TodoManager`
3. The rest of the application remains unchanged

## 🐛 Common Issues & Solutions

### Issue: "Command not found"
**Solution**: Ensure you're in the correct directory and virtual environment is activated

### Issue: "Permission denied" when saving
**Solution**: Check that the `~/.todo-cli` directory is writable

### Issue: "Module not found" errors
**Solution**: Run `pip install -r requirements.txt` to install dependencies

## 📚 Dependencies Explained

- **Typer**: Modern CLI framework that automatically generates help, validates inputs, and provides excellent developer experience
- **Rich**: Terminal formatting library for beautiful tables, panels, and colored output
- **Click**: Underlying framework used by Typer for command-line parsing

## 🎯 Next Steps for Learning

1. **Add more features**: Due dates, tags, task search
2. **Improve data storage**: SQLite database, cloud sync
3. **Add testing**: Unit tests and integration tests
4. **Package the app**: Create a proper Python package with setup.py
5. **Add configuration**: User preferences and customization options

This project demonstrates production-ready Python code with proper structure, documentation, and best practices that you'll encounter in professional software development.
