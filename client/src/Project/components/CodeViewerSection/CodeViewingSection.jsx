import React, {useState} from 'react';
import {useSelector} from "react-redux";

import FunctionCodeTab from "./FunctionCodeTab";
import FunctionCompareTab from "./FunctionCompareTab";
import {selectActiveFunction} from "../../../reducers/activeFunctionSlice";

import TabContainer from 'react-bootstrap/TabContainer'
import TabContent from 'react-bootstrap/TabContent'
import TabPane from 'react-bootstrap/TabPane'
import {Col, Nav, NavLink, NavItem, Row} from "react-bootstrap";

import './CodeViewingSection.scss'

function CodeViewingSection() {

    const [activeTab, setActiveTab] = useState('functionCode');
    const activeFunction = useSelector(selectActiveFunction);

    return (
        <div className="code-view-tab-group-wrapper">
            <TabContainer
                defaultActiveKey="functionCode"
                activeKey={activeTab}
                onSelect={(k) => setActiveTab(k)}
                className="code-view-tab-group"
            >
                <Row>
                    <Col>
                        <Nav variant={"tabs"}>
                            <NavItem>
                                <NavLink eventKey="functionCode">
                                    Function Code
                                </NavLink>
                            </NavItem>
                            {
                                (activeFunction.haveFunctionChanged) && (
                                    <NavItem>
                                        <NavLink eventKey="codeCompare">
                                            Code Compare
                                        </NavLink>
                                    </NavItem>
                                )
                            }
                        </Nav>
                        <Col>
                            <TabContent
                                className="code-view-tab-content"
                            >
                                <TabPane eventKey="functionCode">
                                    <FunctionCodeTab />
                                </TabPane>
                                {
                                    (activeFunction.haveFunctionChanged) && (
                                        <TabPane eventKey="codeCompare">
                                            <FunctionCompareTab />
                                        </TabPane>
                                    )
                                }
                            </TabContent>
                        </Col>
                    </Col>
                </Row>
            </TabContainer>
        </div>
    );
}

function CodeViewingSection2() {

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