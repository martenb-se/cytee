import React, {useState, useEffect, Fragment} from 'react';
import { BrowserRouter, Link, Routes, Route } from 'react-router-dom';
import ProjectSelectionPage from '../Project/pages/ProjectSelectionPage';
import LoadingPage from '../Project/pages/LoadingPage';
import TestCreatorPage from '../Project/pages/TestCreatorPage';
import {updateTime} from '../util/api'


function App() {

    const [currentTime, setCurrentTime] = useState(0);

    useEffect(() => {
        updateTime(setCurrentTime)
    }, []);

    return (
        <div className="App">
            <BrowserRouter>
                <div>{currentTime}</div>

                <Routes>
                    <Route exact path="/" element={<ProjectSelectionPage/>}/>
                    <Route path="/LoadingPage" element={<LoadingPage/>}/>
                    <Route path="/TestCreatorPage" element={<TestCreatorPage/>}/>
                </Routes>
            </BrowserRouter>
        </div>
    );
}

export default App;