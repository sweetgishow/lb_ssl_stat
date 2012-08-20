Ext.require([
    'Ext.form.*',
    'Ext.layout.container.Column',
    'Ext.window.MessageBox',
    'Ext.fx.target.Element',
    'Ext.tab.Panel'
]);


Ext.onReady(function(){

    Ext.define('Ssl', {
        extend: 'Ext.data.Model',
        fields: [
            {name: 'vip_name', type: 'string'},
            {name: 'vip_address', type: 'string'},
            {name: 'cert_expiration_date', type: 'string'},
            {name: 'days_to_expire', type: 'string'},
            {name: 'bit', type: 'string'},
            {name: 'average_connection', type: 'string'},
            {name: 'max_connection', type: 'string'}
        ]
    });
    Ext.define('Lb', {
        extend: 'Ext.data.Model',
        fields: [
            {name: 'average_load', type: 'string'},
            {name: 'average_connection', type: 'int'},
            {name: 'name', type: 'string'},
            {name: 'max_connection', type: 'int'},
            {name: 'lbtype', type: 'string'},
            {name: 'accuracy', type: 'string'},
            {name: 'model', type: 'string'},
            {name: 'os', type: 'string'},
            {name: 'max_load', type: 'string'}
        ]
    });


    Ext.Ajax.request({
        url: '/lb_ssl_stat/d',
        success: function(response){
            var text = Ext.JSON.decode(response.responseText);
            var store = Ext.create('Ext.data.Store', {
                model: 'Lb',
                data: text,
            });

            Ext.create('Ext.grid.Panel', {
                title: 'Loadbalancer SSL Status',
                store: store,
                columns: [
                    {header: "Name", dataIndex: 'name', width: 200},
                    {header: "Type", dataIndex: 'lbtype', width:90},
                    {header: "Model", dataIndex: 'model', width:148},
                    {header: "Os", dataIndex: 'os', width: 90},
                    {header: "Avg Conn", dataIndex: 'average_connection', width: 90},
                    {header: "Max Conn", dataIndex: 'max_connection', width: 90},
                    {header: "Avg Load", dataIndex: 'average_load', width: 90},
                    {header: "Max Load", dataIndex: 'max_load', width: 90},
                    {header: "Accuracy", dataIndex: 'accuracy', width: 90}

                ],
                width: '1000',
                height: 384,
                renderTo: Ext.getBody(),
                listeners: {
                    selectionchange: function(model, records) {
                        ssl_data = records[0].get('ssl');
                        if (ssl_data) {
                            var ssl_store = Ext.create('Ext.data.Store', {
                                model: 'Lb',
                                data: ssl_data,
                            });
                            ssl_detail = Ext.getCmp('ssl_detail');
                            if (ssl_detail){
                                ssl_detail.reconfigure(ssl_store);
                                ssl_detail.setTitle("SSL Detail:&nbsp" + records[0].get('name'));
                                
                            }
                            else {
					            Ext.create('Ext.grid.Panel', {
					                title: "SSL Detail:&nbsp" + records[0].get('name'),
	                                id: 'ssl_detail',
					                store: ssl_store,
					                renderTo: Ext.getBody(),
	                                width: 1000,
					                columns:[
							            {dataIndex: 'vip_name', header: 'Name', width: 298},
							            {dataIndex: 'vip_address', header: 'Address', width: 200},
							            {dataIndex: 'cert_expiration_date', header: 'Cert Exp'},
							            {dataIndex: 'days_to_expire', header: 'DtE'},
							            {dataIndex: 'bit', header: 'Bit'},
							            {dataIndex: 'average_connection', header: 'Avg Conn'},
							            {dataIndex: 'max_connection', header: 'Max conn'}
					                ]
					            });
                            }
                            //this.up('form').getForm().loadRecord(records[0]);
                        }
                    }
                }

            });
            
        }
    });



});

