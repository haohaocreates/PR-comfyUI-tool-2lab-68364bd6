import { ComfyWidgets } from "/scripts/widgets.js";
import { ComfyApp, app } from "/scripts/app.js";
import { api } from '../../../scripts/api.js'

app.registerExtension({
	name: "Comfy.2lab.nodes",
	async beforeRegisterNodeDef(nodeType, nodeData, app) {
        console.log('beforeRegisterNodeDef()')

        // Adds an upload button to the nodes
		if (nodeData?.input?.required?.image?.[1]?.image_upload === true) {
			nodeData.input.required.upload = ["IMAGEUPLOAD"];
		}

		//print workflow output
        const onExecuted = nodeType.prototype.onExecuted
		nodeType.prototype.onExecuted = function (message) {
            onExecuted?.apply(this, arguments)

        }
	},
});

api.addEventListener('execution_start', async ({ detail }) => {
  console.log('#execution_start 2lab', detail)
  //TODO 增加提交到服务器的功能
    try{
        let data = await app.graphToPrompt()
        console.log('api json = ')
//        console.log(data)
        console.log(data.output)
//        const json = JSON.stringify(data.output, null, 2); // convert the data to a JSON string
//        console.log(json)
    } catch (error) {
        console.log('###error', error)
    }
})