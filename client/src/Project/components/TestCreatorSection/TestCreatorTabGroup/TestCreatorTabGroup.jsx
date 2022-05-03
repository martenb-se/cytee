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

import './TestCreatorTabGroup.scss'

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
                    // check if there is anny children with active tab as parent

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
            <div className ="test-creator-tab-group">
                <Tabs
                    id="module-tab-group"
                    className=""
                    onSelect={onSelectCallback}
                    activeKey={activeTabKey}
                >
                    {generateTabList()}
                </Tabs>
            </div>

        </Provider>

    );
}

export default TestCreatorTabGroup;