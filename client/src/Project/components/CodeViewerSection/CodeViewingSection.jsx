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
import {isEmpty} from "lodash";

function CodeViewingSection() {

    const [activeTab, setActiveTab] = useState('functionCode');
    const activeFunction = useSelector(selectActiveFunction);

    function onSelectCallback(k) {
        if (k === activeTab) {
            setActiveTab('');
        } else {
            setActiveTab(k);
        }
    }

    return (
        <>
            {
                (!isEmpty(activeFunction)) &&
                <div className="code-view-tab-group-wrapper">
                    <TabContainer
                        defaultActiveKey="functionCode"
                        activeKey={activeTab}
                        onSelect={onSelectCallback}
                        className="code-view-tab-group"
                    >
                        <Row>
                            <Col>
                                <Nav variant={"tabs"}>
                                    <NavItem>
                                        <NavLink eventKey="functionCode">
                                            Function Code - {activeFunction.fileId}
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
            }
        </>
    );
}

export default CodeViewingSection;