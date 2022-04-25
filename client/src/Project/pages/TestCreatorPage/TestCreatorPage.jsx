import React, {useState} from 'react';

import ProjectExplorerSidebar from '../../components/ProjectExplorerSidebar'
import CodeViewingSection from "../../components/CodeViewerSection";
import TestCreatorSection from "../../components/TestCreatorSection";


function TestCreatorPage({}){

    const [moduleList, setModuleList] = useState([]);

    //testCreationContext

    return (
        <div className = "wrapper">
            <div className = "sidePanel">
                <ProjectExplorerSidebar/>
                <button className ="btn btn-primary">Generate Tests</button>
            </div>
            <div className = "testCreationArea">
                <CodeViewingSection />
                <TestCreatorSection moduleList={moduleList} setModuleList={setModuleList}/>
            </div>
        </div>
    )
}

export default TestCreatorPage;