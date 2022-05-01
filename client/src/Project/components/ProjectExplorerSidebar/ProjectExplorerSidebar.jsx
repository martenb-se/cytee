import React, {useState, useEffect} from 'react';
import TabGroup from "../../../shared/components/TabGroup";
import FunctionListTab from "./FunctionListTab";
import TestListTab from "./TestListTab";

import './ProjectExplorerSidebar.jsx.scss';

function ProjectExplorerSidebar(){

    const [activeTab, setActiveTab] = useState('');

    function getActiveTabComponent() {
        if (activeTab === "Function List") {
            return <FunctionListTab label={'Function Tab'}/>
        } else if (activeTab === "Test List") {
            return  <TestListTab label={'Test List'}/>
        } else {
            return <div className="empty-sidebar-tab"></div>
        }
    }

    function onClickCallback(tabLabel) {
        if (activeTab === tabLabel) {
            setActiveTab('');
        } else if (tabLabel === "Function List") {
            setActiveTab("Function List");
        } else if (tabLabel === "Test List") {
            setActiveTab("Test List");
        }
    }

    return (
        <div className="project-explorer-sidebar-wrapper">
            <div className='project-explorer-sidebar-header'>
                <ul className="nav nav-tabs">
                    <li className="nav-item">
                        <a
                            className={"nav-link " + ((activeTab === "Function List")?"active":"")}
                            aria-current="page"
                            onClick={() => onClickCallback("Function List")}
                        >Function List
                        </a>
                    </li>
                    <li className="nav-item">
                        <a
                            className={"nav-link " + ((activeTab === "Test List")?"active":"")}
                            aria-current="page"
                            onClick={() => onClickCallback("Test List")}
                        >Test List
                        </a>
                    </li>
                </ul>
            </div>
            <div className="project-explorer-sidebar-content">
                {getActiveTabComponent()}
            </div>
        </div>
    );
}
export default ProjectExplorerSidebar