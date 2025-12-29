import React, { useState, useEffect } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, AreaChart, Area } from 'recharts';
import { Plus, Trash2, Cpu, MessageSquare, Save } from 'lucide-react';

function App() {
  // Initialize state from LocalStorage or empty array
  const [expenses, setExpenses] = useState(() => {
    const saved = localStorage.getItem('penny_wise_expenses');
    return saved ? JSON.parse(saved) : [];
  });

  const [newExpense, setNewExpense] = useState({
    date: new Date().toISOString().split('T')[0],
    category: 'Food',
    amount: '',
    description: ''
  });

  const [chatInput, setChatInput] = useState('');
  const [chatHistory, setChatHistory] = useState([
    { role: 'assistant', content: "System Online. Local Storage Active. I can track your spending locally." }
  ]);
  const [loading, setLoading] = useState(false);

  // Save to LocalStorage whenever expenses change
  useEffect(() => {
    localStorage.setItem('penny_wise_expenses', JSON.stringify(expenses));
  }, [expenses]);

  // Add Expense (Client-Side)
  const handleAddExpense = (e) => {
    e.preventDefault();
    if (!newExpense.amount) return;

    const expense = {
      id: Date.now(), // Generate unique ID
      ...newExpense,
      amount: parseFloat(newExpense.amount)
    };

    setExpenses(prev => [...prev, expense]);
    setNewExpense({ ...newExpense, amount: '', description: '' });
  };

  // Chat (Client-Side Simulation)
  const handleChat = (e) => {
    e.preventDefault();
    if (!chatInput) return;

    // User Message
    const userMsg = { role: 'user', content: chatInput };
    setChatHistory(prev => [...prev, userMsg]);
    setLoading(true);
    setChatInput('');

    // Simulated AI Response
    setTimeout(() => {
      let response = "Data stored locally. I cannot process complex queries without a backend.";
      const lowerInput = chatInput.toLowerCase();

      if (lowerInput.includes('total')) {
        const total = expenses.reduce((sum, item) => sum + item.amount, 0);
        response = `Total spending currently logged is $${total.toFixed(2)}.`;
      } else if (lowerInput.includes('hello')) {
        response = "Greetings. I am running in Offline Mode.";
      }

      setChatHistory(prev => [...prev, { role: 'assistant', content: response }]);
      setLoading(false);
    }, 600);
  };

  // Process Data for Charts
  const categoryData = expenses.reduce((acc, curr) => {
    const existing = acc.find(item => item.category === curr.category);
    if (existing) {
      existing.amount += curr.amount;
    } else {
      acc.push({ category: curr.category, amount: curr.amount });
    }
    return acc;
  }, []);

  const totalSpent = expenses.reduce((sum, item) => sum + item.amount, 0);

  return (
    <div className="min-h-screen p-6 text-gray-200" style={{ maxWidth: '1600px', margin: '0 auto' }}>

      {/* HEADER */}
      <header className="mb-8 flex items-center justify-between hud-card">
        <div className="flex items-center gap-4">
          <Cpu className="text-[var(--neon-cyan)]" size={32} />
          <div>
            <h1 className="text-3xl m-0 tracking-widest">PENNY WI$E</h1>
            <p className="text-sm text-[var(--neon-purple)] tracking-[0.3em]">OFFLINE MODE // LOCAL STORAGE</p>
          </div>
        </div>
        <div className="text-right">
          <h2 className="text-2xl">${totalSpent.toFixed(2)}</h2>
          <span className="text-xs uppercase text-gray-500">Total Spent</span>
        </div>
      </header>

      {/* MAIN GRID */}
      <div className="grid grid-cols-12 gap-6">

        {/* LEFT COLUMN - CHARTS (8 cols) */}
        <div className="col-span-12 lg:col-span-8 flex flex-col gap-6">

          <div className="hud-card h-[400px]">
            <h3 className="mb-4 flex items-center gap-2"><div className="w-2 h-2 bg-[var(--neon-purple)]"></div> SPENDING TRENDS</h3>
            <ResponsiveContainer width="100%" height="90%">
              <LineChart data={expenses}>
                <XAxis dataKey="date" stroke="#666" />
                <YAxis stroke="#666" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#000', border: '1px solid var(--neon-cyan)' }}
                  itemStyle={{ color: 'var(--neon-cyan)' }}
                />
                <Line type="monotone" dataKey="amount" stroke="var(--neon-cyan)" strokeWidth={2} dot={{ r: 4, fill: 'black', strokeWidth: 2 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="grid grid-cols-2 gap-6">
            <div className="hud-card h-[300px]">
              <h3 className="mb-4">Category Analysis</h3>
              <ResponsiveContainer width="100%" height="85%">
                <BarChart data={categoryData}>
                  <XAxis dataKey="category" stroke="#666" />
                  <YAxis stroke="#666" />
                  <Tooltip contentStyle={{ backgroundColor: '#000', border: '1px solid var(--neon-green)' }} />
                  <Bar dataKey="amount" fill="var(--neon-purple)" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="hud-card h-[300px] relative flex items-center justify-center">
              <h3 className="absolute top-4 left-4">Distribution Ring</h3>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={categoryData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="amount"
                    stroke="none"
                  >
                    {categoryData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={['#00f3ff', '#bc13fe', '#0aff0a', '#ff003c'][index % 4]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ backgroundColor: '#000', border: '1px solid var(--neon-cyan)' }}
                    itemStyle={{ color: 'var(--neon-cyan)' }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

        </div>

        {/* RIGHT COLUMN - CONTROLS & CHAT (4 cols) */}
        <div className="col-span-12 lg:col-span-4 flex flex-col gap-6">

          {/* Add Expense Form */}
          <div className="hud-card">
            <h3 className="mb-4 border-b border-gray-800 pb-2">INPUT DATA</h3>
            <form onSubmit={handleAddExpense} className="flex flex-col gap-4">
              <div>
                <label className="text-xs text-[var(--neon-cyan)] mb-1 block">DATE</label>
                <input type="date" value={newExpense.date} onChange={e => setNewExpense({ ...newExpense, date: e.target.value })} />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs text-[var(--neon-cyan)] mb-1 block">AMOUNT</label>
                  <input type="number" step="0.01" value={newExpense.amount} onChange={e => setNewExpense({ ...newExpense, amount: e.target.value })} placeholder="0.00" />
                </div>
                <div>
                  <label className="text-xs text-[var(--neon-cyan)] mb-1 block">CATEGORY</label>
                  <select value={newExpense.category} onChange={e => setNewExpense({ ...newExpense, category: e.target.value })}>
                    {["Food", "Transport", "Bills", "Entertainment", "Other"].map(c => <option key={c} value={c}>{c}</option>)}
                  </select>
                </div>
              </div>
              <div>
                <label className="text-xs text-[var(--neon-cyan)] mb-1 block">NOTES</label>
                <input type="text" value={newExpense.description} onChange={e => setNewExpense({ ...newExpense, description: e.target.value })} placeholder="Optional description..." />
              </div>
              <button type="submit" className="mt-2 flex items-center justify-center gap-2">
                <Save size={16} /> SAVE TO LOCAL STORAGE
              </button>
            </form>
          </div>

          {/* AI Chat Terminal */}
          <div className="hud-card flex-grow flex flex-col h-[400px]">
            <h3 className="mb-2 flex items-center gap-2">
              <MessageSquare size={16} className="text-[var(--neon-green)]" /> SYSTEM STATUS
            </h3>
            <div className="flex-grow overflow-y-auto mb-4 bg-black/50 p-2 border border-gray-800 font-mono text-sm">
              {chatHistory.map((msg, idx) => (
                <div key={idx} className={`mb-2 ${msg.role === 'user' ? 'text-right text-[var(--neon-cyan)]' : 'text-left text-[var(--neon-green)]'}`}>
                  <span className="opacity-50 text-xs">[{msg.role === 'user' ? 'USR' : 'SYS'}]</span> {msg.content}
                </div>
              ))}
              {loading && <div className="text-[var(--neon-green)] animate-pulse">:: Processing...</div>}
            </div>
            <form onSubmit={handleChat} className="flex gap-2">
              <input
                type="text"
                value={chatInput}
                onChange={e => setChatInput(e.target.value)}
                placeholder="Enter command..."
                className="flex-grow"
              />
              <button type="submit">CMD</button>
            </form>
          </div>

        </div>

      </div>
    </div>
  );
}

export default App;
