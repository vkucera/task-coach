//
//  TaskViewController.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 15/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "TaskViewController.h"
#import "TaskDetailsController.h"
#import "CategoryViewController.h"

#import "TaskCell.h"
#import "SearchCell.h"
#import "CellFactory.h"

#import "TaskList.h"
#import "Database.h"
#import "Statement.h"

#import "Task.h"

#import "Configuration.h"

#import "DateUtils.h"
#import "i18n.h"

@implementation TaskViewController

@synthesize tableViewController;

- (UITableView *)tableView
{
	return tableViewController.tableView;
}

- (void)willTerminate
{
	[[PositionStore instance] push:self indexPath:nil type:TYPE_SUBTASK searchWord:searchCell.searchBar.text];
}

- (void)loadData
{
	[headers release];

	NSNumber *parentId = nil;
	if (parentTask)
		parentId = [NSNumber numberWithInt:parentTask.objectId];
	
	TaskList *list;
	headers = [[NSMutableArray alloc] initWithCapacity:4];

	NSString *searchWord = nil;
	if ([searchCell.searchBar.text length])
	{
		searchWord = searchCell.searchBar.text;
	}

	list = [[TaskList alloc] initWithView:@"OverdueTask" category:categoryId title:_("Overdue") status:TASKSTATUS_OVERDUE parentTask:parentId searchWord:searchWord];
	if ([list count])
	{
		[headers addObject:list];
	}
	[list release];
	
	list = [[TaskList alloc] initWithView:@"DueSoonTask" category:categoryId title:_("Due soon") status:TASKSTATUS_DUESOON parentTask:parentId searchWord:searchWord];
	if ([list count])
	{
		[headers addObject:list];
	}
	[list release];
	
	list = [[TaskList alloc] initWithView:@"StartedTask" category:categoryId title:_("Started") status:TASKSTATUS_STARTED parentTask:parentId searchWord:searchWord];
	if ([list count])
	{
		[headers addObject:list];
	}
	[list release];
	
	list = [[TaskList alloc] initWithView:@"NotStartedTask" category:categoryId title:_("Not started") status:TASKSTATUS_NOTSTARTED parentTask:parentId searchWord:searchWord];
	if ([list count])
	{
		[headers addObject:list];
	}
	[list release];
}

- (void)restorePosition:(Position *)pos store:(PositionStore *)store
{
	if (pos.searchWord)
	{
		searchCell.searchBar.text = pos.searchWord;
		[self loadData];
		[self.tableView reloadData];
	}
	
	[self.tableView setContentOffset:pos.scrollPosition animated:NO];
	
	if (pos.indexPath)
	{
		switch (pos.type)
		{
			case TYPE_DETAILS:
			{
				[self.tableView selectRowAtIndexPath:pos.indexPath animated:NO scrollPosition:UITableViewScrollPositionNone];
				
				Task *task = [[headers objectAtIndex:pos.indexPath.section] taskAtIndex:pos.indexPath.row];
				TaskDetailsController *ctrl = [[TaskDetailsController alloc] initWithTask:task category:-1];
				[self.navigationController pushViewController:ctrl animated:NO];
				[[PositionStore instance] push:self indexPath:pos.indexPath type:TYPE_DETAILS searchWord:searchCell.searchBar.text];
				[ctrl release];
				
				break;
			}
			case TYPE_SUBTASK:
			{
				Task *task = [[headers objectAtIndex:pos.indexPath.section] taskAtIndex:pos.indexPath.row];
				TaskViewController *ctrl = [[TaskViewController alloc] initWithTitle:task.name category:-1 categoryController:categoryController parentTask:task edit:self.editing];
				[self.navigationController pushViewController:ctrl animated:NO];
				[[PositionStore instance] push:self indexPath:pos.indexPath type:TYPE_SUBTASK searchWord:searchCell.searchBar.text];
				[ctrl release];
				
				[store restore:ctrl];
				
				break;
			}
		}
	}
}

- initWithTitle:(NSString *)theTitle category:(NSInteger)theId categoryController:(CategoryViewController *)controller parentTask:(Task *)parent edit:(BOOL)edit
{
	if (self = [super initWithNibName:@"TaskView" bundle:[NSBundle mainBundle]])
	{
		parentTask = [parent retain];
		shouldEdit = edit;
		title = [theTitle retain];
		categoryId = theId;
		categoryController = controller;
		
		searchCell = [[CellFactory cellFactory] createSearchCell];
		searchCell.searchBar.placeholder = _("Search tasks...");
		searchCell.searchBar.delegate = self;
		
		[self loadData];
	}
	
	return self;
}

- (void)viewDidLoad
{
	self.navigationItem.title = title;
	self.navigationItem.rightBarButtonItem = [self editButtonItem];
	self.editing = shouldEdit;
}

- (void)viewDidUnload
{
	self.tableViewController = nil;
}

- (void)dealloc
{
	[self viewDidUnload];

	[parentTask release];
	[title release];
	[headers release];
	[tapping release];
	[currentCell release];
	[searchCell release];
	
    [super dealloc];
}

- (void)childWasPopped
{
	NSIndexPath *indexPath = [self.tableView indexPathForSelectedRow];
	if (indexPath)
	{
		[self.tableView deselectRowAtIndexPath:indexPath animated:YES];
	}

	[self loadData];
	[self.tableView reloadData];

	if (!isCreatingTask)
		[[PositionStore instance] pop];

	isCreatingTask = NO;
}

- (void)setEditing:(BOOL)editing animated:(BOOL)animated
{
	NSLog(@"Set editing: %d", editing);

	if ([headers count])
	{
		// See editingStyleForRowAtIndexPath. Without this trick, the first task
		// gets an Insert editing style as well as the newly-inserted row.

		if (animated)
			isBecomingEditable = YES;

		[super setEditing:editing animated:animated];
		[self.tableViewController setEditing:editing animated:animated];

		if (editing)
		{
			[self.tableView insertSections:[NSIndexSet indexSetWithIndex:1] withRowAnimation:UITableViewRowAnimationRight];
		}
		else
		{
			[self.tableView deleteSections:[NSIndexSet indexSetWithIndex:1] withRowAnimation:UITableViewRowAnimationRight];
		}
	}
	else
	{
		// There's a mess with the pseudo-section used when the data set is empty...
		[super setEditing:editing animated:animated];
		[self.tableViewController setEditing:editing animated:animated];
		[self.tableView reloadData];
	}
}

- (void)toggleTaskCompletion
{
	NSIndexPath *indexPath = [self.tableView indexPathForCell:currentCell];
	NSInteger section, row;
	
	section = indexPath.section - 1;
	row = indexPath.row;
	if (self.editing)
		section -= 1;
	
	Task *task = [[[headers objectAtIndex:section] taskAtIndex:row] retain];
	
	if ([task taskStatus] == TASKSTATUS_COMPLETED)
	{
		task.completionDate = nil;
		[task save];
	}
	else
	{
		[task setCompleted:YES];
		[task save];
		
		if (![Configuration configuration].showCompleted)
		{
			TaskList *list = [headers objectAtIndex:section];
			[list reload];
			
			if ([list count])
			{
				[self.tableView deleteRowsAtIndexPaths:[NSArray arrayWithObject:indexPath] withRowAnimation:UITableViewRowAnimationBottom];
			}
			else
			{
				[headers removeObjectAtIndex:section];
				if ([headers count])
					[self.tableView deleteSections:[NSIndexSet indexSetWithIndex:indexPath.section] withRowAnimation:UITableViewRowAnimationBottom];
				else
					[self.tableView reloadData];
			}
		}
	}
	
	[currentCell setTask:task target:self action:@selector(onToggleTaskCompletion:)];
	[task release];
	[currentCell release];
	currentCell = nil;
}

- (void)onToggleTaskCompletion:(TaskCell *)cell
{
	currentCell = [cell retain];

	NSIndexPath *indexPath = [self.tableView indexPathForCell:currentCell];
	NSInteger section, row;
	
	section = indexPath.section - 1;
	row = indexPath.row;
	if (self.editing)
		section -= 1;
	
	tapping = [indexPath retain];

	Task *task = [[[headers objectAtIndex:section] taskAtIndex:row] retain];

	if ([Configuration configuration].confirmComplete && ![Configuration configuration].showCompleted)
	{
		UIAlertView *confirm = [[UIAlertView alloc] initWithTitle:_("Confirmation")
	        message:[NSString stringWithFormat:_("Do you really want to mark \"%@\" complete ?"), [task name]] delegate:self
			cancelButtonTitle:_("No") otherButtonTitles:nil];
		[confirm addButtonWithTitle:_("Yes")];
		[confirm show];
		[confirm release];
	}
	else
	{
		[self toggleTaskCompletion];
	}
}

#pragma mark UIAlertViewDelegate protocol

- (void)alertView:(UIAlertView *)alertView didDismissWithButtonIndex:(NSInteger)buttonIndex
{
	if (buttonIndex == 1)
	{
		[self toggleTaskCompletion];
	}
	else
	{
		[currentCell release];
		currentCell = nil;
	}
}

#pragma mark Table view methods

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView
{
	NSInteger count = [headers count] + 1;

	if (self.editing)
	{
		return count + 1;
	}

	NSLog(@"Sections: %d", count);

    return count;
}

- (NSString *)tableView:(UITableView *)tableView titleForHeaderInSection:(NSInteger)section
{
	if (self.editing && (section <= 1))
		return @"";

	if (section == 0)
		return @"";

	if ([headers count])
	{
		return [[headers objectAtIndex:section - (self.editing ? 2 : 1)] title];
	}
	
	return _("No tasks.");
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section
{
	if (self.editing && (section == 1))
	{
		NSLog(@"1 row in section %d", section);

		return 1;
	}

	if (section == 0)
		return 1; // Search cell

	if ([headers count])
	{
		NSInteger count = [[headers objectAtIndex:section - (self.editing ? 2 : 1)] count];
		
		NSLog(@"%d row(s) in section %d", count, section);
		
		return count;
	}

	NSLog(@"No row in section %d", section);

	return 0;
}

- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath
{
	UITableViewCell *cell;

	if (self.editing && (indexPath.section == 1))
	{
		cell = [tableView dequeueReusableCellWithIdentifier:@"Cell"];

		if (cell == nil)
		{
			cell = [[[UITableViewCell alloc] initWithFrame:CGRectZero reuseIdentifier:@"Cell"] autorelease];
		}

#ifdef __IPHONE_3_0
		cell.textLabel.text = 
#else
		cell.text =
#endif
		_("Add task...");
	}
	else if (indexPath.section == 0)
	{
		return searchCell;
	}
	else
	{
		TaskCell *taskCell = (TaskCell *)[tableView dequeueReusableCellWithIdentifier:@"TaskCell"];

		if (taskCell == nil)
		{
			taskCell = [[[CellFactory cellFactory] createTaskCell] autorelease];
		}

		// This is already done in the NIB but when switching to non-editing mode, we
		// must enforce it...
		taskCell.accessoryType = UITableViewCellAccessoryDisclosureIndicator;

		TaskList *list = [headers objectAtIndex:indexPath.section - (self.editing ? 2 : 1)];
		Task *task = [list taskAtIndex:indexPath.row];

		[taskCell setTask:task target:self action:@selector(onToggleTaskCompletion:)];

		cell = (UITableViewCell *)taskCell;
	}

    return cell;
}

- (CGFloat)tableView:(UITableView *)tableView heightForRowAtIndexPath:(NSIndexPath *)indexPath
{
	if (indexPath.section == 0)
		return 44;

	return [Configuration configuration].compactTasks ? 44 : 60;
}

- (UITableViewCellEditingStyle)tableView:(UITableView *)tableView editingStyleForRowAtIndexPath:(NSIndexPath *)indexPath
{
	if (isBecomingEditable)
	{
		if ((indexPath.section == 1) && (indexPath.row == 0))
		{
			isBecomingEditable = NO;
		}

		return (indexPath.section == 0) ? UITableViewCellEditingStyleNone : UITableViewCellEditingStyleDelete;
	}

	if (self.editing)
		switch (indexPath.section)
		{
			case 0:
				return UITableViewCellEditingStyleNone;
			case 1:
				return UITableViewCellEditingStyleInsert;
			default:
				return UITableViewCellEditingStyleDelete;
		}
	
	return (indexPath.section == 0) ? UITableViewCellEditingStyleNone : UITableViewCellEditingStyleDelete;
}

- (BOOL)tableView:(UITableView *)tableView shouldIndentWhileEditingRowAtIndexPath:(NSIndexPath *)indexPath
{
	return indexPath.section != 0;
}

- (void)tableView:(UITableView *)tableView commitEditingStyle:(UITableViewCellEditingStyle)editingStyle forRowAtIndexPath:(NSIndexPath *)indexPath
{
	if ((indexPath.section == 1) && self.editing)
	{
		NSNumber *pid = nil;
		if (parentTask)
			pid = [NSNumber numberWithInt:parentTask.objectId];

		Task *task = [[Task alloc] initWithId:-1 fileId:[Database connection].currentFile name:@"" status:STATUS_NEW taskCoachId:nil description:@""
									startDate:[[DateUtils instance] stringFromDate:[NSDate date]] dueDate:nil completionDate:nil dateStatus:TASKSTATUS_UNDEFINED
									 parentId:pid];
		isCreatingTask = YES;
		TaskDetailsController *ctrl = [[TaskDetailsController alloc] initWithTask:task category:categoryId];
		[self.navigationController pushViewController:ctrl animated:YES];
		[ctrl release];
	}
	else
	{
		Task *task = [[headers objectAtIndex:indexPath.section - (self.editing ? 2 : 1)] taskAtIndex:indexPath.row];
		
		if (task.status == STATUS_NEW)
		{
			// The desktop never head of this one, get rid of it
			[task delete];
		}
		else
		{
			[task setStatus:STATUS_DELETED];
			[task save];
		}

		if ([[headers objectAtIndex:indexPath.section - (self.editing ? 2 : 1)] count] == 1)
		{
			// The whole section is removed
			[headers removeObjectAtIndex:indexPath.section - (self.editing ? 2 : 1)];
			[self.tableView deleteSections:[NSIndexSet indexSetWithIndex:indexPath.section] withRowAnimation:UITableViewRowAnimationFade];
		}
		else
		{
			// The section stays, a row disappears
			[[headers objectAtIndex:indexPath.section - (self.editing ? 2 : 1)] reload];
			[self.tableView deleteRowsAtIndexPaths:[NSArray arrayWithObject:indexPath] withRowAnimation:UITableViewRowAnimationFade];
		}
	}
}

- (IBAction)onAddTask:(UIBarButtonItem *)button
{
	NSNumber *pid = nil;
	if (parentTask)
		pid = [NSNumber numberWithInt:parentTask.objectId];

	Task *task = [[Task alloc] initWithId:-1 fileId:[Database connection].currentFile name:@"" status:STATUS_NEW taskCoachId:nil description:@""
								startDate:[[DateUtils instance] stringFromDate:[NSDate date]] dueDate:nil completionDate:nil dateStatus:TASKSTATUS_UNDEFINED
								 parentId:pid];
	isCreatingTask = YES;
	TaskDetailsController *ctrl = [[TaskDetailsController alloc] initWithTask:task category:categoryId];
	[self.navigationController pushViewController:ctrl animated:YES];
	[ctrl release];
}

- (IBAction)onSync:(UIBarButtonItem *)button
{
	[categoryController setWantSync];

	[self.navigationController popToRootViewControllerAnimated:YES];
}

- (void)tableView:(UITableView *)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath
{
	if (tapping && ([tapping compare:indexPath] == NSOrderedSame))
	{
		[self.tableView deselectRowAtIndexPath:tapping animated:NO];
		[tapping release];
		tapping = nil;

		return;
	}

	if ((self.editing && indexPath.section == 1) || (indexPath.section == 0))
	{
		[self onAddTask:nil];
		return;
	}

	Task *task = [[headers objectAtIndex:indexPath.section - (self.editing ? 2 : 1)] taskAtIndex:indexPath.row];
	TaskDetailsController *ctrl = [[TaskDetailsController alloc] initWithTask:task category:-1];
	[self.navigationController pushViewController:ctrl animated:YES];
	[[PositionStore instance] push:self indexPath:[NSIndexPath indexPathForRow:indexPath.row inSection:(indexPath.section - (self.editing ? 2 : 1))] type:TYPE_DETAILS searchWord:searchCell.searchBar.text];
	[ctrl release];
}

- (void)tableView:(UITableView *)tableView accessoryButtonTappedForRowWithIndexPath:(NSIndexPath *)indexPath
{
	Task *task = [[headers objectAtIndex:indexPath.section - (self.editing ? 2 : 1)] taskAtIndex:indexPath.row];
	TaskViewController *ctrl = [[TaskViewController alloc] initWithTitle:task.name category:-1 categoryController:categoryController parentTask:task edit:self.editing];
	[[PositionStore instance] push:self indexPath:[NSIndexPath indexPathForRow:indexPath.row inSection:(indexPath.section - (self.editing ? 2 : 1))] type:TYPE_SUBTASK searchWord:searchCell.searchBar.text];
	[self.navigationController pushViewController:ctrl animated:YES];
	[ctrl release];
}

// UISearchBarDelegate

- (void)searchBarSearchButtonClicked:(UISearchBar *)searchBar
{
	[searchBar resignFirstResponder];

	[self loadData];
	[self.tableView reloadData];
}

- (void)searchBarCancelButtonClicked:(UISearchBar *)searchBar
{
	searchBar.text = @"";

	[searchBar resignFirstResponder];

	[self loadData];
	[self.tableView reloadData];
}

@end
