import React, {useContext} from "react";
import {unsavedTestInfoContext, moduleNameMapper} from "../TestCreatorSection";


function ModulePanel() {
    return (
        <div className ="modulePanel-wrapper">
            <ModuleSelector />
            <ModuleList />
        </div>
    )
}

function ModuleSelector() {
    const [state, dispatch] = useContext(unsavedTestInfoContext);

    function addModule(moduleName) {
        dispatch({
            type: 'moduleData/addModule',
            payload: moduleName
        });
    }

    return (
        <div className='dropdown'>
            <button className="btn btn-secondary dropdown-toggle" type="button" id="dropdownMenuButton1"
                    data-bs-toggle="dropdown" aria-expanded="false">
                Add Module
            </button>
            <ul className="dropdown-menu" aria-labelledby="dropdownMenuButton1">
                <li><button className="dropdown-item" onClick ={ () => addModule('argumentList')}>Arguments</button></li>
                <li><button className="dropdown-item" onClick ={ () => addModule('returnValue')}>Return Value</button></li>
                <li><button className="dropdown-item" onClick ={ () => addModule('exception')}>Exception</button></li>
            </ul>
        </div>
    );
}

function ModuleList() {
    const [state, dispatch] = useContext(unsavedTestInfoContext);

    function deleteModule(moduleName) {
        dispatch({
            type: 'moduleData/removeModule',
            payload: moduleName
        })
    }

    return (
        <table>
            <thead>
            <tr><td>Modules</td></tr>
            </thead>
            <tbody>
            {
                Object.keys(state.moduleData).sort().map( moduleName => {
                    return (
                        <tr key={moduleName}><td>{moduleNameMapper[moduleName]}</td>
                            <td>
                                <button onClick={() => deleteModule(moduleName)}>
                                    X
                                </button>
                            </td>
                        </tr>
                    )
                })
            }
            </tbody>
        </table>
    )
}

export default ModulePanel;