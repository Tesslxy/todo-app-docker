import { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

function App() {
  const [todos, setTodos] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({ title: "", description: "" });

  // Fetch todos on component mount
  useEffect(() => {
    fetchTodos();
  }, []);

  const fetchTodos = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(`${API_URL}/todos`);
      setTodos(response.data);
    } catch (err) {
      setError("Failed to fetch todos: " + err.message);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.title.trim()) {
      setError("Title is required");
      return;
    }

    try {
      const response = await axios.post(`${API_URL}/todos`, formData);
      setTodos([...todos, response.data]);
      setFormData({ title: "", description: "" });
      setError(null);
    } catch (err) {
      setError("Failed to create todo: " + err.message);
      console.error(err);
    }
  };

  const handleToggleTodo = async (todo) => {
    try {
      const response = await axios.put(`${API_URL}/todos/${todo.id}`, {
        completed: !todo.completed,
      });
      setTodos(todos.map((t) => (t.id === todo.id ? response.data : t)));
    } catch (err) {
      setError("Failed to update todo: " + err.message);
      console.error(err);
    }
  };

  const handleDeleteTodo = async (todoId) => {
    try {
      await axios.delete(`${API_URL}/todos/${todoId}`);
      setTodos(todos.filter((t) => t.id !== todoId));
    } catch (err) {
      setError("Failed to delete todo: " + err.message);
      console.error(err);
    }
  };

  return (
    <div className="container">
      <h1>📝 Todo App</h1>

      {error && <div className="error">{error}</div>}

      <form onSubmit={handleSubmit} className="form">
        <input
          type="text"
          placeholder="Todo title..."
          value={formData.title}
          onChange={(e) => setFormData({ ...formData, title: e.target.value })}
          className="input"
        />
        <input
          type="text"
          placeholder="Description (optional)..."
          value={formData.description}
          onChange={(e) =>
            setFormData({ ...formData, description: e.target.value })
          }
          className="input"
        />
        <button type="submit" className="button">
          Add Todo
        </button>
      </form>

      {loading ? (
        <p>Loading...</p>
      ) : (
        <div className="todos-list">
          {todos.length === 0 ? (
            <p className="empty">No todos yet. Create one to get started!</p>
          ) : (
            todos.map((todo) => (
              <div
                key={todo.id}
                className={`todo-item ${todo.completed ? "completed" : ""}`}
              >
                <div className="todo-content">
                  <input
                    type="checkbox"
                    checked={todo.completed}
                    onChange={() => handleToggleTodo(todo)}
                    className="checkbox"
                  />
                  <div>
                    <h3>{todo.title}</h3>
                    {todo.description && <p>{todo.description}</p>}
                  </div>
                </div>
                <button
                  onClick={() => handleDeleteTodo(todo.id)}
                  className="delete-button"
                >
                  Delete
                </button>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}

export default App;
