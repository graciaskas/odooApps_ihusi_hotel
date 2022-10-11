-> 13.0.0.1 

fix method for create vendor bill.


--> 13.0.0.2
in pos receipt not show branches
orders payment not show branches

--> 13.0.0.3
-> Remove pos feature from branch module.


--> 13.0.0.4
-> Solve issue for inventory adjustment when valuation is set automatic.

--> 13.0.0.5
-> Add branch field in picking type related to stock.warehouse and updated the rule from global to user's current branch only for branch user.

--> 13.0.0.6
-> Remove account invoice ref from wizard, update code for sale advanced payment and
pass branch field.

--> 13.0.0.7
-> Call super in all possible methods.
-> Update context all for order lines like sale, purchase, invoice, move and bank statement lines.

Version: 13.0.0.8 | Date : 22/09/2020
-> Give option to select default branch in header and pass selected branch to the records.

Date 23rd sept 2020
version 13.0.0.9
issue solve:-
	- when user need to click two time otherwise need to reload manually , if want to change branch.

Version 13.0.1.0 : (23/10/20)
		- Update _assign_picking() method as per base.

Version 13.0.1.1 : (28/12/20)
-- Fixed the multi branch record issue to display only the selected branch records

Version 13.0.1.2 : (08/01/21)
-- Fixed the multi branch record issue

Version 13.0.1.3 : (26/01/21)
-- Added warning message while change the branch that is not active

Version 13.0.1.4 : (29/01/21)
-- Record not create if you try from the another branch that is not set as default, fix it.

=> 13.0.1.5 : Add language translate with index.
13.0.1.6 ==>fixed issue of manager rule for branch.
13.0.1.7 ==>fixed issue of user access in purchase,inventory and invoice.

13.0.1.8 ==> fixed issue of register payment warning with user.

date 12/05/21
versio 13.0.1.9
	- invoice , bill , credit note , debit note user show all branch records.

date 15/07/21
version 13.0.2.0
issue solve:-
	- all modules show branch according to company


date 16/07/21
version 13.0.3.0
issue solve:-
	- allowed branch only select in default branch. 

=> 13.0.3.1 : Add French, Spanish , Arabic and Dutch translation in module also improved an index.

=> 13.0.3.2 : Pass branch in account move correct, two view name same for different object changed it and fixed.


13.0.3.3 ==>fixed issue of sale records for Personal Orders which shows only user records. 

13.0.3.4 ==>fixed issue of traceback for record rules when uninstall module.

13.0.3.5 ==>assigned automatically "Branch/Manager" access to Administrator user after module installed and when create new user as  it's works for all other apps i.e purchase, sale, pos etc 

date 1/07/2022
version 13.0.3.6
issue solve:-
	call super in session_info method.

13.0.3.7 ==>fixed issue of changed write method of res user in upgraded addons. 