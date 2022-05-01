import React, {useState, useEffect} from 'react';
import {selectUnsavedActiveTest} from "../../../../reducers/activeTestInfoSlice";
import {useSelector} from "react-redux";
import ArgumentTab from "../ArgumentTab";
import ReturnTab from "../ReturnTab";
import ExceptionTab from "../ExceptionTab";
import {isEmpty, cloneDeep} from "lodash";

import ObjectCreationTab from "../objectCreationTab/ObjectCreationTab";

function TestCreatorTabGroup() {

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