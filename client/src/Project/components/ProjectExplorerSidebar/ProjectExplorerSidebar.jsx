import React from 'react';
import TabGroup from "../../../shared/components/TabGroup";
import functionTabGenerator from "./FunctionsTab";
import testTabGenerator from "./TestsTab";


function ProjectExplorerSidebar(){

    return (
        <>
            <div className={"projectExplorerSidebar-wrapper"}>
                <TabGroup
                    tabList={[functionTabGenerator(), testTabGenerator()]}
                />
            </div>
        </>
    );
}

export default ProjectExplorerSidebar