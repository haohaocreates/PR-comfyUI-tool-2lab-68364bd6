import { ComfyWidgets } from "/scripts/widgets.js";
import { ComfyApp, app } from "/scripts/app.js";
import { api } from '../../../scripts/api.js'

app.registerExtension({
	name: "Comfy.2lab.nodes",
	async beforeRegisterNodeDef(nodeType, nodeData, app) {

        // Adds an upload button to the nodes
		if (nodeData?.input?.required?.image?.[1]?.image_upload === true) {
			nodeData.input.required.upload = ["IMAGEUPLOAD"];
		}

    if (nodeData.name === "PublishWorkflow (2lab)") {
        const widgets_count = 5;          //PublishWorkflow初始状态是5个参数
        function populate(text) {
            console.log('populate() nodeData = ',nodeData.name)
            console.log('text = ',text)
            // 移除在初始状态上增加的widgets
            if (this.widgets) {
                console.log('widgets_count = ',widgets_count)
                console.log('this.widgets.length = ',this.widgets.length)
                for (let i = widgets_count; i < this.widgets.length; i++) {
                    this.widgets[i].onRemove?.();
                }
                this.widgets.length = widgets_count;
            }

            const v = [...text];
            console.log('v = ',v)
//            console.log('v.length = ',v.length)
//            if (!v[0]) {
//                v.shift();
//            }
            var url = ''
            if(v.length == 1){      //from class PublishWorkflow
                url = v[0];
                console.log('url = ',url)
                const w = ComfyWidgets["STRING"](this, "text", ["STRING", { multiline: true }], app).widget;
                w.inputEl.readOnly = true;
                w.inputEl.style.opacity = 0.6;
                w.value = url;

                requestAnimationFrame(() => {
                    const sz = this.computeSize();
                    if (sz[0] < this.size[0]) {
                        sz[0] = this.size[0];
                    }
                    if (sz[1] < this.size[1]) {
                        sz[1] = this.size[1];
                    }
                    this.onResize?.(sz);
                    app.graph.setDirtyCanvas(true, false);
                });
           }
        }

        // When the node is executed we will be sent the input text, display this in the widget
        const onExecuted = nodeType.prototype.onExecuted;
        nodeType.prototype.onExecuted = function (message) {
            onExecuted?.apply(this, arguments);
            populate.call(this, message.text);
        };

        const onConfigure = nodeType.prototype.onConfigure;
        nodeType.prototype.onConfigure = function () {
//            console.log('onConfigure()',)
//            console.log('nodeData.name = ',nodeData.name)

            onConfigure?.apply(this, arguments);
            if (this.widgets_values?.length) {
                populate.call(this, this.widgets_values);
            }
        };
    }
  },
});

api.addEventListener('execution_start', async ({ detail }) => {
  console.log('#execution_start 2lab', detail)
    try{
        let wf = await app.graphToPrompt()
        console.log('wf.output = ',wf.output)

        const data = wf.output;
        // 使用函数查找class_type为"PublishWorkflow (2lab)"的节点的publish值
         for (const key in data) {
            console.log('key = ',key)
            if (data.hasOwnProperty(key)) {
              console.log('class_type = ',data[key].class_type)
              if (data[key].class_type === 'PublishWorkflow (2lab)') {
                 console.log('data[key].inputs.publish = ',data[key].inputs.publish)
                 if(data[key].inputs.publish){
                    var jsonString = JSON.stringify(data);
                    var url = 'http://www.2lab.cn/pb/uploadWorkflow?w='+encodeURIComponent(jsonString)
                    var newWindow = window.open(url, '_blank');
                 }else{
                    return
                 }
              }
            }
          }
    } catch (error) {
        console.log('###error', error)
    }
})

