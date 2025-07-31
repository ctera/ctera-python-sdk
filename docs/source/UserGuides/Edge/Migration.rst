=========
Migration
=========

.. automethod:: cterasdk.edge.ctera_migrate.CTERAMigrate.list_shares
   :noindex:

.. code-block:: python

   """ List all shares available on a source host """
   credentials = edge_types.HostCredentials('source-hostname', 'username', 'password')
   edge.ctera_migrate.list_shares(credentials)

   """ List all shares available on the current Edge Filer """
   credentials = edge_types.HostCredentials.localhost()
   edge.ctera_migrate.list_shares(credentials)

.. automethod:: cterasdk.edge.ctera_migrate.CTERAMigrate.list_tasks
   :noindex:

.. code-block:: python

   """ Print all tasks, optional flag to list deleted tasks """
   for task in edge.ctera_migrate.list_tasks(deleted=False):
       print(task)

.. automethod:: cterasdk.edge.ctera_migrate.CTERAMigrate.start
   :noindex:

.. code-block:: python

   edge.ctera_migrate.start(task)

.. automethod:: cterasdk.edge.ctera_migrate.CTERAMigrate.stop
   :noindex:

.. code-block:: python

   edge.ctera_migrate.stop(task)

.. automethod:: cterasdk.edge.ctera_migrate.CTERAMigrate.delete
   :noindex:

.. code-block:: python

   edge.ctera_migrate.delete(edge.ctera_migrate.list_tasks())  # delete all tasks

.. automethod:: cterasdk.edge.ctera_migrate.CTERAMigrate.restore
   :noindex:

.. code-block:: python

   edge.ctera_migrate.restore(edge.ctera_migrate.list_tasks(deleted=True))  # recover all deleted tasks

.. automethod:: cterasdk.edge.ctera_migrate.CTERAMigrate.details
   :noindex:

.. code-block:: python

   edge.ctera_migrate.details(task)

.. automethod:: cterasdk.edge.ctera_migrate.CTERAMigrate.results
   :noindex:

.. code-block:: python

   """Retrieve tasks and all jobs associated with a task"""
   tasks = edge.ctera_migrate.list_tasks()
   jobs = edge.ctera_migrate.details(tasks[0])

   """Retrieve the results of a job execution"""
   edge.ctera_migrate.results(tasks[0], jobs[0])
   edge.ctera_migrate.results(tasks[0], jobs[0], export=True)  # export to file
   edge.ctera_migrate.results(tasks[0], jobs[0], export=True, destination='c:/users/bwayne/downloads/discovery.csv')

.. automethod:: cterasdk.edge.ctera_migrate.CTERAMigrate.log
   :noindex:

.. code-block:: python

   """Retrieve tasks and all jobs associated with a task"""
   tasks = edge.ctera_migrate.list_tasks()
   jobs = edge.ctera_migrate.details(tasks[0])

   """Retrieve the results of a job execution"""
   edge.ctera_migrate.log(tasks[0], jobs[0])
   edge.ctera_migrate.log(tasks[0], jobs[0], share='smb-project-nexus')  # export to file
   edge.ctera_migrate.log(tasks[0], jobs[0], share='smb-project-nexus', destination='c:/users/bwayne/downloads/discovery.csv')

Discovery
=========

.. automethod:: cterasdk.edge.ctera_migrate.Discovery.list_tasks
   :noindex:

.. code-block:: python

   """ Print all discovery tasks, optional flag to list deleted tasks """
   for task in edge.ctera_migrate.discovery.list_tasks(deleted=False):
       print(task)

.. automethod:: cterasdk.edge.ctera_migrate.Discovery.add
   :noindex:

.. code-block:: python

   credentials = edge_types.HostCredentials('source-hostname', 'username', 'password')
   task = edge.ctera_migrate.discovery.add('my-discovery', credentials, ['share1', 'share2'], auto_start=False, log_every_file=True, notes='job 1')


   """Add a local discovery task"""
   credentials = edge_types.HostCredentials.localhost()
   task = edge.ctera_migrate.discovery.add('my-discovery', credentials, ['share1', 'share2'], log_every_file=True, notes='local discovery job')

   """Run the task"""
   edge.ctera_migrate.start(task)

.. automethod:: cterasdk.edge.ctera_migrate.Discovery.update
   :noindex:


Migration
=========

.. automethod:: cterasdk.edge.ctera_migrate.Migration.list_tasks
   :noindex:

.. code-block:: python

   """ Print all migration tasks, optional flag to list deleted tasks """
   for task in edge.ctera_migrate.migration.list_tasks(deleted=False):
       print(task)

.. automethod:: cterasdk.edge.ctera_migrate.Migration.add
   :noindex:

.. code-block:: python

   credentials = edge_types.HostCredentials('source-hostname', 'username', 'password')
   task = edge.ctera_migrate.migration.add('my-discovery', credentials, ['share1', 'share2'], auto_start=False, winacls=True, cloud_folder='my_cloud_folder', create_cloud_folder_per_share=False, compute_checksum=False, exclude=['*.pdf', '*.jpg'], include=['*.png', '*.avi'], notes='migration job 1')

   """Run the task"""
   edge.ctera_migrate.start(task)
