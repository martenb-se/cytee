import React, {useContext, useEffect} from "react";
import {addModuleData, removeModuleData, selectUnsavedActiveTest} from "../../../../reducers/activeTestInfoSlice";
import {selectActiveFunction} from "../../../../reducers/activeFunctionSlice";
import {moduleNameMapper} from "../TestCreatorSection";
import {isEmpty} from "lodash";

import {useSelector, useDispatch} from "react-redux";

import './ModulePanel.scss'

function ModulePanel() {
    return (
        <div className ="module-panel-wrapper h-100 border-end">
            <ModuleSelector />
            <ModuleList/>
        </div>
    )
}

function ModuleSelector() {

    const activeFunction = useSelector(selectActiveFunction);
    const dispatch = useDispatch();

    function addModule(moduleName) {
        dispatch(addModuleData({
            moduleName: moduleName,
            activeFunction: activeFunction,
        }));
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

    const unsavedTest = useSelector(selectUnsavedActiveTest);
    const dispatch = useDispatch();

    function deleteModule(moduleName) {
        dispatch(removeModuleData(moduleName));
    }

    return (
        <table className="table">
            <thead>
            <tr><td>Modules</td></tr>
            </thead>
            <tbody>
            { (!isEmpty(unsavedTest)) &&
                Object.keys(unsavedTest.moduleData).sort().map( moduleName => {
                    return (
                        <tr key={moduleName}><td>{moduleNameMapper[moduleName]}</td>
                            <td>
                                <button
                                    type="button"
                                    className="btn-close"
                                    aria-label="close"
                                    onClick={() => deleteModule(moduleName)}>

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