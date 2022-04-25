import React from 'react';

function TabGroup({tabList, activeTab, setActiveTab}) {

    function getActiveTab() {
        let foundTab = tabList.find(tab => tab.name === activeTab );
        if (!foundTab)
            return <div></div>;
        return foundTab.content;
    }

    return (
        <div className="TabGroup">
            <div className="TabGroup-header">
                <ul>
                    {tabList.map(tab => <li onClick={() => setActiveTab(tab.name)} key={tab.name}>{tab.tabName}</li>)}
                </ul>
            </div>
            <div className="TabGroup-content">
                {getActiveTab()}
            </div>
        </div>
    )
}

export default TabGroup;