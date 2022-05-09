import React, {useContext, useEffect, useState} from 'react';
import {selectUnsavedActiveTest} from "../../../../reducers/activeTestInfoSlice";
import {useSelector} from "react-redux";
import ArgumentTab from "../ArgumentTab";
import ReturnTab from "../ReturnTab";
import ExceptionTab from "../ExceptionTab";
import {isEmpty} from "lodash";

import ObjectCreationTab from "../objectCreationTab/ObjectCreationTab";

import {localTabGroupContext} from "../TestCreatorSection";

import TabContainer from 'react-bootstrap/TabContainer'
import TabContent from 'react-bootstrap/TabContent'
import TabPane from 'react-bootstrap/TabPane'
import {Nav, NavItem, NavLink, Row} from "react-bootstrap";

import './TestCreatorTabGroup.scss'

function TestCreatorTabGroup({}) {

    const unsavedTest = useSelector(selectUnsavedActiveTest);
    const [activeTabKey, setActiveTabKey] = useState('');
    const [localTabState, ] = useContext(localTabGroupContext);

    useEffect(() => {

        const moduleNames = Object.keys(unsavedTest.moduleData);
        if (moduleNames.length > 0) {
            if (activeTabKey !== '') {
                if (moduleNames.findIndex(moduleName => moduleName === activeTabKey) === -1)
                    setActiveTabKey(moduleNames[0]);

            } else {
                setActiveTabKey(moduleNames[0]);
            }
        } else {
            if (activeTabKey !== '')
                setActiveTabKey('');
        }
    }, [unsavedTest])

    function onSelectCallback(k) {
        setActiveTabKey(k);
    }

    function generateTabNavLinks() {
        if (!isEmpty(unsavedTest)) {
            const TabComponentList = Object.keys(unsavedTest.moduleData).sort().map(moduleName => {
                switch (moduleName) {
                    case 'argumentList':
                        return (
                            <NavItem key="argumentList">
                                <NavLink eventKey="argumentList">Argument List</NavLink>
                            </NavItem>
                        );
                    case 'returnValue':
                        return (
                            <NavItem key="returnValue">
                                <NavLink eventKey="returnValue">Return Value</NavLink>
                            </NavItem>
                        );
                    case 'exception':
                        return (
                            <NavItem key="exception">
                                <NavLink eventKey="exception">Exception</NavLink>
                            </NavItem>
                        );
                }
            });

            if ((localTabState.length > 0)) {
                TabComponentList.push(...(localTabState.map(childTab => {
                    return (
                        <NavItem key={childTab.eventKey}>
                            <NavLink key={childTab.eventKey} eventKey={childTab.eventKey}>{childTab.title}</NavLink>
                        </NavItem>
                    )
                })));
            }
            return TabComponentList;
        } else {
            return (
                <NavItem key="key">
                    <NavLink key="key" eventKey=""></NavLink>
                </NavItem>
            )
        }
    }

    function generateTabContent() {
        if (!isEmpty(unsavedTest)) {
            const TabComponentList = Object.keys(unsavedTest.moduleData).sort().map(moduleName => {
                switch (moduleName) {
                    case 'argumentList':
                        return (
                            <TabPane className="h-100" key="argumentList" eventKey="argumentList">
                                <ArgumentTab/>
                            </TabPane>
                        );
                    case 'returnValue':
                        return (
                            <TabPane className="h-100" key="returnValue" eventKey="returnValue">
                                <ReturnTab/>
                            </TabPane>
                        );
                    case 'exception':
                        return (
                            <TabPane className="h-100" key="exception" eventKey="exception">
                                <ExceptionTab/>
                            </TabPane>
                        );
                }
            });

            if ((localTabState.length > 0)) {
                TabComponentList.push(...(localTabState.map(childTab => {
                    return (
                        <TabPane key={childTab.eventKey} eventKey={childTab.eventKey}>
                            <ObjectCreationTab
                                initBaseState={childTab.initValue}
                                onChangeCallback={childTab.onObjectChangeCallback}
                            />
                        </TabPane>
                    )
                })));
            }

            return TabComponentList;
        } else {
            return (
                <TabPane key="bib">
                    <div></div>
                </TabPane>
            )
        }
    }

    return (
        <div className="test-creator-tab-group flex-grow-1 d-flex flex-column">
            <TabContainer
                id="module-tab-group"
                className="col flex-grow-1"
                onSelect={onSelectCallback}
                activeKey={activeTabKey}
            >
                <Row>
                    <Nav className="h-100" variant={"tabs"}>
                        {generateTabNavLinks()}
                    </Nav>
                </Row>
                <Row className="flex-grow-1">
                    <TabContent className="h-100">
                        {generateTabContent()}
                    </TabContent>
                </Row>


            </TabContainer>

        </div>
    );
}

export default TestCreatorTabGroup;