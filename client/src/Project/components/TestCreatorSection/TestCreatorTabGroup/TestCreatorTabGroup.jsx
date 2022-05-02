import React, {useState, useEffect, createContext, useReducer} from 'react';
import {selectUnsavedActiveTest} from "../../../../reducers/activeTestInfoSlice";
import {useSelector} from "react-redux";
import ArgumentTab from "../ArgumentTab";
import ReturnTab from "../ReturnTab";
import ExceptionTab from "../ExceptionTab";
import {isEmpty, cloneDeep} from "lodash";

import ObjectCreationTab from "../objectCreationTab/ObjectCreationTab";

import Tabs from 'react-bootstrap/Tabs'
import Tab from 'react-bootstrap/Tab'
import TabContainer from 'react-bootstrap/TabContainer'
import TabContent from 'react-bootstrap/TabContent'
import TabPane from 'react-bootstrap/TabPane'

const initLocalTabState = [];

export const localTabGroupContext = createContext();
const { Provider } = localTabGroupContext;

function localTabGroupReducer(state, action) {
    switch(action.type) {
        case 'addChildTab':
            const addChildLocalTabsClone = cloneDeep(state);
            console.log('addChildLocalTabsClone: ',  addChildLocalTabsClone);
            if (addChildLocalTabsClone.findIndex(childTab => childTab.eventKey === action.payload.eventKey) === -1) {
                addChildLocalTabsClone.push(cloneDeep(action.payload));
            }
            return addChildLocalTabsClone;
        case 'removeChildTab':
            const removeChildLocalTabsClone = cloneDeep(state);
            console.log('removeChildLocalTabsClone: ',  removeChildLocalTabsClone);
            const childIndex = removeChildLocalTabsClone.findIndex(childTab => childTab.eventKey === action.payload);
            if (childIndex !== -1) {
                removeChildLocalTabsClone.splice(childIndex, 1);
            }
            return removeChildLocalTabsClone
    }
}

function TestCreatorTabGroup({}) {

    const unsavedTest = useSelector(selectUnsavedActiveTest);

    const [activeTabKey, setActiveTabKey] = useState('');

    const [localTabState, localTabDispatch] = useReducer(localTabGroupReducer, initLocalTabState);

    useEffect(() => {

        const moduleNames = Object.keys(unsavedTest.moduleData);
        if (moduleNames.length > 0) {

            // If so, Is active tab selected

            if (activeTabKey !== '') {

                // If it is selected, check if it still is in the module data
                if (moduleNames.findIndex(moduleName => moduleName === activeTabKey) === -1) {
                    // If not set it to the next tab in line
                    setActiveTabKey(moduleNames[0]);
                }
            } else {
                // If active tab is not selected, set it to the first tab.
                setActiveTabKey(moduleNames[0]);
            }
        } else {
            if (activeTabKey !== '') {
                setActiveTabKey('');
            }
        }
    }, [unsavedTest])

    function onSelectCallback(k) {
        setActiveTabKey(k);
    }

    function generateTabList() {
        if (!isEmpty(unsavedTest)) {
            const TabComponentList = Object.keys(unsavedTest.moduleData).sort().map( moduleName => {
                switch (moduleName) {
                    case 'argumentList':
                        return (
                            <Tab key="argumentList" eventKey="argumentList" title="Argument List">
                                <ArgumentTab />
                            </Tab>
                        );
                    case 'returnValue':
                        return (
                            <Tab key="returnValue" eventKey="returnValue" title="Return Value">
                                <ReturnTab />
                            </Tab>
                        );
                    case 'exception':
                        return (
                            <Tab key="exception" eventKey="exception" title="Exception">
                                <ExceptionTab />
                            </Tab>
                        );
                }
            });

            if ((localTabState.length > 0)) {
                TabComponentList.push(...(localTabState.map(childTab => {
                    return (
                        <Tab key={childTab.eventKey} eventKey={childTab.eventKey} title={childTab.title}>
                            <ObjectCreationTab
                                initBaseState={childTab.initValue}
                                onChangeCallback={childTab.onObjectChangeCallback}
                            />
                        </Tab>
                    )
                })));
            }

            return TabComponentList;
        } else {
            return <div></div>
        }
    }

    return (
        <Provider value={[localTabState, localTabDispatch]}>
            <Tabs
                id="module-tab-group"
                className="mb-3"
                onSelect={onSelectCallback}
                activeKey={activeTabKey}
            >
                {generateTabList()}
            </Tabs>
        </Provider>

    );




}

function TestCreatorTabGroup2() {

    const unsavedTest = useSelector(selectUnsavedActiveTest);
    const [tabList, setTabList] = useState([]);
    const [activeTab, setActiveTab] = useState(undefined);
    const [parentToChildTabMap, setParentToChildTabMap] = useState([]);

    function onClickCallback(tabLabel) {
        setActiveTab(tabLabel);
    }

    function getActiveTabComponent() {
        if (tabList.length > 0) {
            const tabData = tabList.find(tab => tab.props.label === activeTab);

            if (tabData === undefined) {

                if (parentToChildTabMap.length > 0) {
                    const childTabData = parentToChildTabMap.find(childData => childData.label === activeTab);

                    if (childTabData !== undefined) {
                        // TODO: Consider adding the parent label
                        return (
                            <ObjectCreationTab
                                label={childTabData.label}
                                initBaseState={childTabData.initValue}
                                onChangeCallback={childTabData.onObjectChangeCallback}
                            />
                        )
                    } else {
                        console.log('asdasdasdadsaddkhjdbfgkjdrbk');
                        return <div></div>
                    }
                }
            }
            return tabData;

            //return tabList.find(tab => tab.props.label === activeTab);
        } else {
            return <div className="empty-test-creator-tab"></div>
        }
    }

    function addChildTab(childTabData) {
        const parentToChildTabMapCopy = cloneDeep(parentToChildTabMap);
        parentToChildTabMapCopy.push(childTabData);
        setParentToChildTabMap(parentToChildTabMapCopy);
    }

    function removeChildTab(childTab) {
        const parentToChildTabMapCopy = cloneDeep(parentToChildTabMap);
        for (let i = 0; i < parentToChildTabMapCopy.length; i++) {
            if (parentToChildTabMapCopy.label === childTab) {
                parentToChildTabMapCopy.splice(i, 1);
                break;
            }
        }
        setParentToChildTabMap(parentToChildTabMapCopy);
    }



    useEffect(() => {
        if (!isEmpty(unsavedTest)) {
            const tabComponentList = Object.keys(unsavedTest.moduleData).sort().map(moduleName => {
                switch (moduleName) {
                    case 'argumentList':
                        return <ArgumentTab label="Argument List" addChildFunction={addChildTab} removeChildFunction={removeChildTab}/>
                    case 'returnValue':
                        return <ReturnTab label="Return Value" addChildFunction={addChildTab} removeChildFunction={removeChildTab}/>
                    case 'exception':
                        return <ExceptionTab label="Exception"/>
                }
            });
            setTabList(tabComponentList);
        }
    }, [unsavedTest])

    useEffect(() => {
        if (tabList.length > 0) {

            if (activeTab === undefined) {
                setActiveTab(tabList[0].props.label);
            } else  {
                if (tabList.findIndex(tab => tab.props.label === activeTab) === -1) {
                    if (parentToChildTabMap.findIndex(childTab => childTab.label === activeTab) === -1) {
                        setActiveTab(tabList[0].props.label);
                    }
                }
            }
        } else {
            setActiveTab(undefined);
        }
    }, [tabList, parentToChildTabMap])

    useEffect(() => {

    }, [])

    return (
        <div className ="test-creator-tab-group-wrapper">
            <div className ="test-creator-tab-group-header">
                <ul className="nav nav-tabs">
                    {
                        tabList.map(tab => {
                            return (
                                <li className="nav-item" key={tab.props.label}>
                                    <a
                                        className={"nav-link " + ((tab.props.label === activeTab)?"active":"")}
                                        aria-current="page"
                                        onClick={() => onClickCallback(tab.props.label)}
                                    >
                                        {tab.props.label}
                                    </a>
                                </li>
                            )}
                        )
                    }
                    {
                        parentToChildTabMap.map(childTab => {
                            return (
                                <li className="nav-item" key={childTab.label}>
                                    <a
                                        className={"nav-link " + ((childTab.label === activeTab)?"active":"")}
                                        aria-current="page"
                                        onClick={() => onClickCallback(childTab.label)}
                                    >
                                        {childTab.label}
                                    </a>
                                </li>
                            )
                        })
                    }
                </ul>
            </div>
            <div className ="test-creator-tab-group-content">
                {
                    getActiveTabComponent()
                }
            </div>
        </div>
    )
}

export default TestCreatorTabGroup;