import React from 'react';

import TabGroup from "../../../shared/components/TabGroup";
import functionCodeTabGenerator from "./FunctionCodeTab";
import FunctionCompareTab from "./FunctionCompareTab";

function CodeViewingSection() {

    return (
        <>
            <div>CodeViewingSection</div>
            <TabGroup tabList={[functionCodeTabGenerator(), <FunctionCompareTab label={'Function compare view'}/>]} />
        </>
    )
}

export default CodeViewingSection