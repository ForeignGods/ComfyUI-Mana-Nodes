import { app } from "../../../scripts/app.js";
import { ComfyWidgets } from "../../../scripts/widgets.js";

app.registerExtension({
    name: "ManaNodes.string2file",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "Save/Preview Text") {
            function populate(values) {

				let previewText;
				if (values.length === 1) {
					// If the function is called during execution, use the first index
					previewText = values[0];
				} else {
					// If the function is called during configuration, use the third index
					previewText = values[2];
				}
				let previewWidget = this.widgets.find(w => w.name === "preview");
				if (!previewWidget) {
					// Create preview widget if it does not exist
					previewWidget = ComfyWidgets["STRING"](this, "preview", ["STRING", { multiline: true }], app).widget;
					previewWidget.inputEl.readOnly = false;
					previewWidget.inputEl.style.opacity = 0.6;
				}
				previewWidget.value = previewText; // Set or update the value
			
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

            const onExecuted = nodeType.prototype.onExecuted;
            nodeType.prototype.onExecuted = function (message) {
                onExecuted?.apply(this, arguments);
                populate.call(this, message.text);
            };

            const onConfigure = nodeType.prototype.onConfigure;
            nodeType.prototype.onConfigure = function () {
                onConfigure?.apply(this, arguments);
                if (this.widgets_values?.length) {
                    populate.call(this, this.widgets_values);
                }
            };
        }
    },
});