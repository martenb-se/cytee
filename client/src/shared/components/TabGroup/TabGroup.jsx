import React, {useState, useEffect} from 'react';

function TabGroup({tabList, setActiveTabCallback}) {

    const [activeTab, setActiveTab] = useState(undefined);
    const [tabLabelList, setTabLabelList] = useState([]);

    function setActiveTabFunc(tabLabel) {
        setActiveTab(tabLabel);
        //setActiveTabCallback(tabLabel);
    }

    function getActiveTab() {
        let foundTab = tabList.find(tab => tab.props.label === activeTab);
        if (!foundTab) {
            return <div></div>
        }
        return foundTab;
    }

    function generateTabLabelList() {
        const newTabList = [];
        for (const tab of tabList) {
            newTabList.push(tab.props.label);
        }
        return newTabList;
    }

    useEffect(() => {

    }, [])

    useEffect(() => {
        if (tabList.length > 0) {
            if (tabList.length > tabLabelList.length) {
                 for (const tab of tabList) {
                     if (tabLabelList.indexOf(tab.props.label) === -1) {
                        setActiveTab(tab.props.label);
                     }
                 }
            }

            setTabLabelList(generateTabLabelList());
        } else {
            setTabLabelList([]);
        }

    }, [tabList])

    useEffect(() => {

        if (tabLabelList.length > 0) {

            if ((activeTab === undefined) || tabLabelList.indexOf(activeTab) === -1) {
                setActiveTab(tabLabelList[0]);
            }

        } else if (tabLabelList.length === 0) {
            setActiveTab(undefined);
        }

    }, [tabLabelList])

    useEffect(() => {

    }, [activeTab])

    return (
        <div className="TabGroup">
            <div className="TabGroup-header">
                <ul>
                    {
                        ((tabLabelList.length > 0) && tabLabelList.sort().map(label => {
                            return (
                                <li
                                    key={label}
                                    onClick={() => setActiveTabFunc(label)}
                                >
                                    {label}
                                </li>);
                        }))
                    }
                </ul>
            </div>
            <div>
                {getActiveTab()}
            </div>
        </div>
    );
}

export default TabGroup;