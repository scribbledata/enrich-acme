{% extends 'README_DEFAULT.md' %} 

{% block specificdescription %}
{% endblock %}

{% block specificconfiguration %} 

Base class for a Indexer transform. For now only one action is
supported 'copy'. More actions will be added in future.

    Example::

	    {
		"transform": "HDIPIndexer",
		"enable": true,
		"dependencies": {
                   ....
		},
		"args": {
                   "db": "%(data_root)s/shared/audit/index.tinydb",
                   "collections": "datasets",
                   "include_runs": True 
                }
            }

{% endblock %} 

{% block specificoutputs %} 
{% endblock  %} 

{% block specificdependencies %} 
{% endblock  %} 
 
