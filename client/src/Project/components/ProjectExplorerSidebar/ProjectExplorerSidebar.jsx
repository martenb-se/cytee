import React, {useState, useEffect} from 'react';
import FunctionListTab from "./FunctionListTab";
import TestListTab from "./TestListTab";

import './ProjectExplorerSidebar.jsx.scss';

import TabContainer from 'react-bootstrap/TabContainer'
import TabContent from 'react-bootstrap/TabContent'
import TabPane from 'react-bootstrap/TabPane'
import {Col, Nav, NavLink, NavItem, Row} from "react-bootstrap";


export function FileNameTableRow({fileName, colSpan, haveFunctionChanged}) {
    return (
      <tr className ="table-secondary">
        <td
            title={fileName}
            colSpan={colSpan}
        >
            <div className ="d-flex flex-row justify-content-sm-between">
                <span className="bold">
                    {formatTableString(fileName, 32)}
                </span>
                <div>
                    <span className={(haveFunctionChanged)?"badge bg-warning":"badge bg-success"}>
                        {(haveFunctionChanged)?'Changed':'Up To Date'}
                    </span>
                </div>

            </div>
        </td>
      </tr>
    );
}


export function formatTableString(string, maxLength) {
    let formattedString;
    if (string.length >= maxLength) {
        formattedString = string.substring(string.length-(maxLength-3), string.length);
        formattedString = '...' + formattedString;
    } else {
        formattedString = string;
    }
    return formattedString;
}

export function categorizeList(list, key) {
    const categorizedList = {};
    for (const item of list) {
        if (categorizedList[item[key]] === undefined) {
            categorizedList[item[key]] = [];
        }
        categorizedList[item[key]].push(item);
    }
    return categorizedList;
}

function ProjectExplorerSidebar() {

    const [selectedTab, setSelectedTab] = useState('functionList');

    function onSelectCallback(k) {
        if (k === selectedTab) {
            setSelectedTab('');
        } else {
            setSelectedTab(k);
        }
    }

    return (
        <div className="container project-explorer-sidebar-wrapper ">
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
                                <TabPane className="h-100" eventKey={'functionList'}>
                                    <FunctionListTab />
                                </TabPane>
                                <TabPane className="h-100" eventKey={'testList'}>
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

export default ProjectExplorerSidebar