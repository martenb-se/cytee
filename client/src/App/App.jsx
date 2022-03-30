import React, {useState, useEffect, Fragment} from 'react';
import { BrowserRouter, Link, Routes, Route } from 'react-router-dom';


function App() {
    const [currentTime, setCurrentTime] = useState(0);

    useEffect(() => {
        fetch('/api/time').then(res => res.json()).then(data => {
            setCurrentTime(data.time);
        });
    }, []);

    return (
        <div className="App">
         {currentTime}
        </div>
    );
}

export default App;