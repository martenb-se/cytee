import React, {useState} from 'react';
import {useSelector} from "react-redux";

import FunctionCodeTab from "./FunctionCodeTab";
import FunctionCompareTab from "./FunctionCompareTab";
import {selectActiveFunction} from "../../../reducers/activeFunctionSlice";

function CodeViewingSection() {

    const [activeTab, setActiveTab] = useState('Function Code');
    const activeFunction = useSelector(selectActiveFunction);

    function getActiveComponentTab() {
        if (activeTab === 'Function Code') {
            return <FunctionCodeTab label={'Function Code'}/>
        } else if (activeTab === 'Compare Code') {
            return <FunctionCompareTab label={'Compare Code'}/>
        } else {
            return <div className="empty-code-viewing-section"></div>
        }
    }

    function onClickCallback(tabLabel) {
        setActiveTab(tabLabel);
    }

    return (
        <div className ="code-view-tab-group-wrapper">
            <div className ="project-explorer-sidebar-header">
                <ul className="nav nav-tabs">
                    <li className ="nav-item">
                        <a
                            className={"nav-link " + ((activeTab === "Function Code")?"active":"")}
                            aria-current="page"
                            onClick={() => onClickCallback("Function Code")}
                        >
                            Function Code
                        </a>
                    </li>
                    {
                        (activeFunction.haveFunctionChanged) && (
                            <li>
                                <a
                                    className={"nav-link " + ((activeTab === "Compare Code")?"active":"")}
                                    aria-current="page"
                                    onClick={() => onClickCallback("Compare Code")}
                                >
                                    Compare Code
                                </a>
                            </li>
                        )
                    }

                </ul>
            </div>
            <div className ="project-explorer-sidebar-content">
                {getActiveComponentTab()}
            </div>
        </div>
    );

}

export default CodeViewingSection;