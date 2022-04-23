import React from 'react';

function TestCreatorSection(){
    return (
        <>
            <div className = "moduleData-wrapper">
                <ModuleSelector />
            </div>
        </>
    )
}

function ModuleSelector(){
    return (
        <>
            <div className="dropdown">
                <button className="btn btn-secondary dropdown-toggle" type="button" id="dropdownMenuButton1"
                        data-bs-toggle="dropdown" aria-expanded="false">
                    Dropdown button
                </button>
                <ul className="dropdown-menu" aria-labelledby="dropdownMenuButton1">
                    <li><a className="dropdown-item" href="#">Action</a></li>
                    <li><a className="dropdown-item" href="#">Another action</a></li>
                    <li><a className="dropdown-item" href="#">Something else here</a></li>
                </ul>
            </div>
            <select className = "form-select">
                <option>arguments</option>
                <option>return value</option>
                <option>exception</option>
            </select>
            <p>Modules</p>
            <ul>
                <li>args</li>
                <li>return value</li>
            </ul>
        </>
    )
}

export default TestCreatorSection