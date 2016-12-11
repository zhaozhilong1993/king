.. king documentation master file, created by
   sphinx-quickstart on Sun Dec 11 15:51:04 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

      Licensed under the Apache License, Version 2.0 (the "License"); you may
      not use this file except in compliance with the License. You may obtain
      a copy of the License at

          http://www.apache.org/licenses/LICENSE-2.0

      Unless required by applicable law or agreed to in writing, software
      distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
      WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
      License for the specific language governing permissions and limitations
      under the License.

.. _create-a-stack:

Creating your first order
=========================

Confirming you can access a King endpoint
-----------------------------------------

Before any King commands can be run, your cloud credentials need to be
sourced::

    $ source openrc

You can confirm that King is available with this command::

    $ king service-list

Your can see the running status of king.

Preparing to create a order
---------------------------

Your cloud will have different flavors and images available for
launching instances, you can discover what is available by running::

    $ openstack flavor list
    $ openstack image list
    $ openstack volume list
