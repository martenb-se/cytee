import React from 'react';

import TabGroup from "../../../shared/components/TabGroup";
import functionCodeTabGenerator from "./FunctionCodeTab";

function CodeViewingSection() {

    return (
        <>
            <div>CodeViewingSection</div>
            <TabGroup tabList={[functionCodeTabGenerator()]} />
        </>
    )
}

export default CodeViewingSection