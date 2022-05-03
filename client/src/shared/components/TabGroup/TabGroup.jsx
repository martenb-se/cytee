import React, {useState, useEffect, createContext, useContext, useReducer} from 'react';
import cloneDeep from "lodash/cloneDeep";
import {unsavedTestInfoReducer} from "../../../Project/components/TestCreatorSection/unsavedTestInfoReducer";

export const groupTabContext = createContext();
const {Provider} = groupTabContext;

const initGroupTabContext = {
    activeTab: undefined,
    tabs:[],
    tabsOldLength: 0,
    tabLabelList: [],
    childTabs: [],
    childTabsOldLength: 0,
    parentChildMap: {},
}

function tabGroupReducerFunction(state, action) {
    switch(action.type) {


        case 'setActiveTab':
            const newSetActiveTabState = cloneDeep(state);
            newSetActiveTabState.activeTab = cloneDeep(action.payload);
            //const newSetActiveTabState = state;
            //newSetActiveTabState.parentChildMap = JSON.parse(JSON.stringify(state.parentChildMap));
            //newStateActiveTabState.activeTab = actin
            return newSetActiveTabState;

        case 'setTabs':
            const newSetTabsState = cloneDeep(state);
            newSetTabsState.tabs =  action.payload;

            if (newSetTabsState.tabs.length > 0) {
                if (newSetTabsState.tabs.length > state.tabLabelList.length) {
                    for (const tab of newSetTabsState.tabs) {
                        if (state.tabLabelList.indexOf(tab.props.label) === -1) {
                            newSetTabsState.activeTab = tab.props.label
                        }
                    }
                }

                newSetTabsState.tabLabelList = [];
                for (const tab of newSetTabsState.tabs) {
                    newSetTabsState.tabLabelList.push(tab.props.label);
                }

            } else {
                newSetTabsState.tabLabelList = [];
                //setTabLabelList([]);
            }

            return newSetTabsState;


        case 'setTabLabelList':
            const newSetTabLabelListState = cloneDeep(state);
            newSetTabLabelListState.tabLabelList = action.payload;
            return newSetTabLabelListState;


        case 'generateTabLabelList':
            const newGenerateTabLabelListState = cloneDeep(state);
            newGenerateTabLabelListState.tabLabelList = [];
            for (const tab of tabs) {
                newGenerateTabLabelListState.tabLabelList.push(tab.props.label);
            }
            return newGenerateTabLabelListState.sort();


        case 'addChildTab':
            const newAddChildTabState = cloneDeep(state);
            newAddChildTabState.parentChildMap[action.payload.parent][action.payload.label] = {
                value: action.payload.value,
                onChangeCallback: action.payload.onChangeCallback,
            }
            newAddChildTabState.childTabs.push(action.payload.component);
            newAddChildTabState.tabLabelList.push(action.payload.label).sort();
            newAddChildTabState.activeTab = action.payload.label;
            return newAddChildTabState;


        case 'removeChildTab':
            const newRemoveChildTabState = cloneDeep(state);
            // Remove from labelList
            const  childIndex = newRemoveChildTabState.tabLabelList.indexOf(action.payload);
            newRemoveChildTabState.tabLabelList.splice(childIndex, 1);

            // Remove from child tabs
            const childComponentIndex = newRemoveChildTabState.tabLabelList.findIndex(comp => comp.props.label === action.payload);
            newRemoveChildTabState.tabLabelList.splice(childComponentIndex, 1);

            // Remove from parentChildMap
            const parentKeyList = Object.keys(newRemoveChildTabState.parentChildMap);
            let parentComponent = '';
            for (const parent in parentKeyList) {
                if (action.payload in newRemoveChildTabState.parentChildMap[parent]) {
                    parentComponent = parent;
                    break;
                }
            }
            delete newRemoveChildTabState.parentChildMap[parentComponent][action.payload];

            // Handle situation where child tab is active tab
            if (newRemoveChildTabState.activeTab === action.payload) {
                if (tabLabelList.length < 0) {
                    newRemoveChildTabState.ativeTab = tabLabelList[0];
                } else {
                    newRemoveChildTabState.ativeTab = undefined;
                }
            }
            return newRemoveChildTabState;


        default:
            throw new Error();


    }
}

function TabGroup({tabList, setActiveTabCallback}) {

    //const [activeTab, setActiveTab] = useState(undefined);
    //const [tabLabelList, setTabLabelList] = useState([]);

    const [tabGroupState, tabGroupReducer] = useReducer(tabGroupReducerFunction, initGroupTabContext);
    //const [unsavedTestInfoState, unsavedTestInfoDispatch] = useReducer(unsavedTestInfoReducer, initialState);

    useEffect(() => {
        tabGroupReducer({
            type: 'setTabs',
            payload: tabList,
        })
    }, [tabList])

    function getActiveTabComponent() {
        let foundTab = tabGroupState.tabs.find(tab => tab.props.label === tabGroupState.activeTab);
        if (!foundTab) {
            return <div></div>
        }
        return foundTab;
    }

    function generateTabLabelList() {
        const newTabList = [];
        for (const tab of newSetTabsState.tabs) {
            newTabList.push(tab.props.label);
        }
        return newTabList;
    }

    useEffect(() => {
        console.log('tabGroupState: ', tabGroupState);
    }, [tabGroupState])


    useEffect(() => {

        if (tabGroupState.tabLabelList.length > 0) {

            if ((tabGroupState.activeTab === undefined) || tabGroupState.tabLabelList.indexOf(tabGroupState.activeTab) === -1) {
                //setActiveTab(tabGroupState.tabLabelList[0]);
                tabGroupReducer({
                    type: 'setActiveTab',
                    payload: tabGroupState.tabLabelList[0]
                });
            }

        } else if (tabGroupState.tabLabelList.length === 0) {
            tabGroupReducer({
                type: 'setActiveTab',
                payload: undefined,
            });
            //setActiveTab(undefined);
        }

    }, [tabGroupState.tabLabelList])

    useEffect(() => {

    }, [tabGroupState.activeTab])

    return (
        <Provider value={[tabGroupState, tabGroupReducer]}>
            <div className="TabGroup">
                <div className="TabGroup-header">
                    <ul>
                        {
                            ((tabGroupState.tabLabelList.length > 0) && tabGroupState.tabLabelList.sort().map(label => {
                                return (
                                    <li
                                        key={label}
                                        onClick={() => tabGroupReducer({type:'setActiveTab', payload:label})}
                                    >
                                        {label}
                                    </li>);
                            }))
                        }
                    </ul>
                </div>
                <div>
                    {getActiveTabComponent()}
                </div>
            </div>
        </Provider>
    );
}

export default TabGroup;