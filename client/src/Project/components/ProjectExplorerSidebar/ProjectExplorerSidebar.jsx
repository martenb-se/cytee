import React, {useState, useEffect} from 'react';
import TabGroup from "../../../shared/components/TabGroup";
import FunctionListTab from "./FunctionListTab";
import TestListTab from "./TestListTab";

import './ProjectExplorerSidebar.jsx.scss';

import Tabs from "react-bootstrap/Tabs";
import Tab from "react-bootstrap/Tab";
import TabContainer from 'react-bootstrap/TabContainer'
import TabContent from 'react-bootstrap/TabContent'
import TabPane from 'react-bootstrap/TabPane'
import {Col, Nav, NavLink, NavItem, Row} from "react-bootstrap";


function ProjectExplorerSidebar() {

    const [selectedTab, setSelectedTab] = useState('functionList');

    function onSelectCallback(k) {
        if (k === selectedTab) {
            console.log('asdasd');
            setSelectedTab('');
        } else {
            setSelectedTab(k);
        }
    }

    return (
        <div className="container project-explorer-sidebar-wrapper">
            <TabContainer
                id="project-explorer-sidebar-tab-container"
                defaultActiveKey={selectedTab}
                activeKey={selectedTab}
                onSelect={onSelectCallback}
            >
                <Row>
                    <Col md='auto'>
                        <Nav className="flex-column" variant={"pills"}>
                            <NavItem >
                                <NavLink className="sidebar-nav-link" eventKey="functionList">Function List</NavLink>
                            </NavItem>
                            <NavItem>
                                <NavLink className="sidebar-nav-link" eventKey="testList">Test List</NavLink>
                            </NavItem>
                        </Nav>
                    </Col>
                    { (selectedTab !== '') &&
                        <Col>
                            <TabContent className="sidebar-tab-content">
                                <TabPane eventKey={'functionList'}>
                                    <FunctionListTab />
                                </TabPane>
                                <TabPane eventKey={'testList'}>
                                    <TestListTab />
                                </TabPane>
                            </TabContent>
                        </Col>
                    }
                </Row>
            </TabContainer>
        </div>

    )
}


function ProjectExplorerSidebar2(){

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