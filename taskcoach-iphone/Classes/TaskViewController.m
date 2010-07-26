//
//  TaskViewController.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 15/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "ODCalendarDayTimelineView.h"
#import "NSDate+TKCategory.h"

#import "TaskCoachAppDelegate.h"

#import "TaskViewController.h"
#import "ParentTaskViewController.h"
#import "TaskDetailsController.h"
#import "TaskDetailsControlleriPad.h"
#import "CategoryViewController.h"
#import "PaperHeaderView.h"

#import "TaskCell.h"
#import "TaskCelliPad.h"
#import "SearchCell.h"
#import "CellFactory.h"

#import "Configuration.h"

#import "CDTask.h"
#import "CDTask+Addons.h"
#import "CDDomainObject+Addons.h"
#import "CDFile.h"

#import "DateUtils.h"
#import "NSDate+Utils.h"
#import "i18n.h"
#import "LogUtils.h"

#import "CalendarTaskView.h"

#define ADJUSTSECTION (self.editing ? 2 : 1)

static void deleteTask(CDTask *task)
{
	for (CDTask *child in [task children])
		deleteTask(child);
	[task delete];
}

@interface TaskViewController ()

- (void)populate;
- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView;
- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section;

@end;

@implementation TaskViewController

@synthesize tableViewController;
@synthesize calendarView;
@synthesize calendarSearch;
@synthesize toolbar;
@synthesize categoryController;
@synthesize groupButton;
@synthesize popCtrl;

@synthesize headerView;

- (UITableView *)tableView
{
	return tableViewController.tableView;
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)toInterfaceOrientation
{
	if (groupSheet)
		groupSheet.hidden = YES;

	return YES;
}

- (void)didRotateFromInterfaceOrientation:(UIInterfaceOrientation)fromInterfaceOrientation
{
	self.calendarView.scrollView.frame = self.view.frame;
	[self.calendarView reloadDay];
	[self.calendarView.timelineView setNeedsDisplay];
	
	[groupSheet showFromBarButtonItem:self.groupButton animated:NO];
}

- (NSPredicate *)predicate
{
	return nil;
}

- (void)willTerminate
{
	[[PositionStore instance] push:self indexPath:nil type:TYPE_SUBTASK searchWord:searchCell.searchBar.text];
}

- (NSInteger)calendarButtonIndex
{
	for (NSInteger idx = 0; idx < [self.toolbar.items count]; ++idx)
		if ([[self.toolbar.items objectAtIndex:idx] tag] == 1)
			return idx;
	assert(0);
}

- (void)restorePosition:(Position *)pos store:(PositionStore *)store
{
	[self populate];
	
	if ((pos.indexPath.section >= [self numberOfSectionsInTableView:self.tableView]) ||
		(pos.indexPath.row >= [self tableView:self.tableView numberOfRowsInSection:pos.indexPath.section]))
		return;
	
	if (pos.searchWord)
	{
		searchCell.searchBar.text = pos.searchWord;

		[self populate];
		[self.calendarView reloadDay];
	}
	
	if ([Configuration configuration].viewStyle == STYLE_TABLE)
		[self.tableView setContentOffset:pos.scrollPosition animated:NO];
	else
		[self.calendarView.scrollView setContentOffset:pos.scrollPosition animated:NO];

	if (pos.indexPath)
	{
		switch (pos.type)
		{
			case TYPE_DETAILS:
			{
				[self.tableView selectRowAtIndexPath:pos.indexPath animated:NO scrollPosition:UITableViewScrollPositionNone];

				CDTask *task = [results objectAtIndexPath:pos.indexPath];

				UIViewController *ctrl;
				if (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPhone)
					ctrl = [[TaskDetailsController alloc] initWithTask:task tabIndex:pos.tab];
				else
					ctrl = [[TaskDetailsControlleriPad alloc] initWithTask:task];

				[self.navigationController pushViewController:ctrl animated:NO];
				[[PositionStore instance] push:self indexPath:pos.indexPath type:TYPE_DETAILS searchWord:searchCell.searchBar.text];
				[ctrl release];
				
				break;
			}
			case TYPE_SUBTASK:
			{
				CDTask *task = [results objectAtIndexPath:pos.indexPath];
				ParentTaskViewController *ctrl = [[ParentTaskViewController alloc] initWithCategoryController:categoryController edit:self.editing parent:task];
				[self.navigationController pushViewController:ctrl animated:NO];
				[[PositionStore instance] push:self indexPath:pos.indexPath type:TYPE_SUBTASK searchWord:searchCell.searchBar.text];
				[ctrl release];
				
				[store restore:ctrl];
				
				break;
			}
		}
	}
}

- initWithCategoryController:(CategoryViewController *)controller edit:(BOOL)edit
{
	if ((self = [super initWithNibName:@"TaskView" bundle:[NSBundle mainBundle]]))
	{
		shouldEdit = edit;
		categoryController = controller;
		
		searchCell = [[CellFactory cellFactory] createSearchCell];
		searchCell.searchBar.placeholder = _("Search tasks...");
		searchCell.searchBar.delegate = self;
	}

	return self;
}

- initWithCoder:(NSCoder *)coder
{
	if ((self = [super initWithCoder:coder]))
	{
		if (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPad)
		{
			searchCell = [[CellFactory cellFactory] createSearchCell];
			searchCell.searchBar.placeholder = _("Search tasks...");
			searchCell.searchBar.delegate = self;
		}
	}

	return self;
}

- (void)populate
{
	[results release];

	NSFetchRequest *request = [[NSFetchRequest alloc] init];
	[request setEntity:[NSEntityDescription entityForName:@"CDTask" inManagedObjectContext:getManagedObjectContext()]];

	NSMutableArray *preds = [[NSMutableArray alloc] init];
	[preds addObject:[NSPredicate predicateWithFormat:@"status != %d", STATUS_DELETED]];

	if ([searchCell.searchBar.text length])
	{
		[preds addObject:[NSPredicate predicateWithFormat:@"name CONTAINS[cd] %@ OR longDescription CONTAINS[cd] %@",
						  searchCell.searchBar.text, searchCell.searchBar.text]];
	}
	else
	{
		if (![Configuration configuration].showCompleted)
			[preds addObject:[NSPredicate predicateWithFormat:@"dateStatus != %d", TASKSTATUS_COMPLETED]];
		if (![Configuration configuration].showInactive)
			[preds addObject:[NSPredicate predicateWithFormat:@"dateStatus != %d", TASKSTATUS_NOTSTARTED]];

		[preds addObject:[self predicate]];
	}

	[preds addObject:[NSPredicate predicateWithFormat:@"file = %@", [Configuration configuration].cdCurrentFile]];

	[request setPredicate:[NSCompoundPredicate andPredicateWithSubpredicates:preds]];
	[preds release];

	if (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPhone)
	{
		// All of this for nothing. CoreData bug: if the underlying SQL query matches several times the same object,
		// NSFetchedResultsController uniques them but gets confused because countForFetchRequest does not! This leads
		// to NSRangeExceptions though the logic is perfectly valid... This happens only on the iPhone...
		
		NSArray *tasks;
		NSError *error;
		tasks = [getManagedObjectContext() executeFetchRequest:request error:&error];
		if (!tasks)
		{
			UIAlertView *alert = [[UIAlertView alloc] initWithTitle:@"Error" message:@"Could not fetch tasks" delegate:self cancelButtonTitle:@"OK" otherButtonTitles:nil];
			[alert show];
			[alert release];
		
			results = nil;
			return;
		}

		[request setPredicate:[NSPredicate predicateWithFormat:@"SELF IN %@", tasks]];
	}

	NSString *grouping;
	NSString *sorting;

	switch ([Configuration configuration].taskGrouping)
	{
		case GROUP_STATUS:
			grouping = @"dateStatus";
			sorting = @"dateStatus";
			break;
		case GROUP_PRIORITY:
			grouping = @"priority";
			sorting = @"priority";
			break;
		case GROUP_START:
			grouping = @"startDateOnly";
			sorting = @"startDate";
			break;
		case GROUP_DUE:
			grouping = @"dueDateOnly";
			sorting = @"dueDate";
			break;
	}

	NSSortDescriptor *sd1 = [[NSSortDescriptor alloc] initWithKey:sorting ascending:![Configuration configuration].reverseGrouping];
	NSSortDescriptor *sd2 = [[NSSortDescriptor alloc] initWithKey:@"name" ascending:YES];
	[request setSortDescriptors:[NSArray arrayWithObjects:sd1, sd2, nil]];
	[sd1 release];
	[sd2 release];
	
	NSLog(@"Object count: %d", [getManagedObjectContext() countForFetchRequest:request error:nil]);

	results = [[NSFetchedResultsController alloc] initWithFetchRequest:request managedObjectContext:getManagedObjectContext() sectionNameKeyPath:grouping cacheName:nil];
	results.delegate = self;

	NSError *error;
	if (![results performFetch:&error])
	{
		UIAlertView *alert = [[UIAlertView alloc] initWithTitle:@"Error" message:@"Could not fetch tasks"@ delegate:self cancelButtonTitle:@"OK" otherButtonTitles:nil];
		[alert show];
		[alert release];

		[results release];
		results = nil;
	}

	[request release];
}

- (void)viewDidLoad
{
	if (self.editing != shouldEdit)
		self.editing = shouldEdit;

	self.calendarView.delegate = self;
	self.calendarView.scrollView.autoresizingMask = UIViewAutoresizingFlexibleWidth|UIViewAutoresizingFlexibleHeight;
	self.calendarView.timelineView.autoresizingMask = UIViewAutoresizingFlexibleWidth|UIViewAutoresizingFlexibleHeight;
	self.calendarView.scrollView.frame = self.view.frame;
	self.calendarSearch.placeholder = _("Search tasks...");
	self.calendarSearch.text = searchCell.searchBar.text;

	if ([Configuration configuration].viewStyle == STYLE_TABLE)
	{
		self.navigationItem.rightBarButtonItem = [self editButtonItem];
		self.tableView.hidden = NO;
		self.calendarView.hidden = YES;
		self.calendarSearch.hidden = YES;

		NSMutableArray *items = [NSMutableArray arrayWithArray:self.toolbar.items];
		UIBarButtonItem *btn = [[UIBarButtonItem alloc] initWithImage:[UIImage imageNamed:@"switchcal.png"] style:UIBarButtonItemStyleBordered target:self action:@selector(onSwitch:)];
		btn.tag = 1;
		[items replaceObjectAtIndex:[self calendarButtonIndex] withObject:btn];
		[btn release];
		[self.toolbar setItems:items animated:NO];
	}
	else
	{
		self.navigationItem.rightBarButtonItem = nil;
		self.tableView.hidden = YES;
		self.calendarView.hidden = NO;
		self.calendarSearch.hidden = NO;
		
		NSMutableArray *items = [NSMutableArray arrayWithArray:self.toolbar.items];
		UIBarButtonItem *btn = [[UIBarButtonItem alloc] initWithImage:[UIImage imageNamed:@"switchtable.png"] style:UIBarButtonItemStyleBordered target:self action:@selector(onSwitch:)];
		btn.tag = 1;
		[items replaceObjectAtIndex:[self calendarButtonIndex] withObject:btn];
		[btn release];
		[self.toolbar setItems:items animated:NO];
	}

	NSDate *nextUpdate = [NSDate dateRounded];
	nextUpdate = [nextUpdate addTimeInterval:60];
	minuteTimer = [[NSTimer alloc] initWithFireDate:nextUpdate interval:60 target:self selector:@selector(onMinuteTimer:) userInfo:nil repeats:YES];
	[[NSRunLoop currentRunLoop] addTimer:minuteTimer forMode:NSDefaultRunLoopMode];

	if (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPad)
		self.tableView.separatorStyle = UITableViewCellSeparatorStyleNone;
}

// Timer instantiation and destruction is done here instead
// of viewDidLoad/viewDidUnload because in this case the controller
// is never freed (the timer keeps a ref on it)

- (void)viewDidUnload
{
	self.tableViewController = nil;
	self.calendarView = nil;
	self.calendarSearch = nil;
	self.toolbar = nil;
	self.headerView = nil;

	[results release];
	results = nil;

	[minuteTimer invalidate];
	[minuteTimer release];
	minuteTimer = nil;
}

- (void)onChangeGrouping:(UIBarButtonItem *)button
{
	if (popCtrl)
	{
		[popCtrl dismissPopoverAnimated:YES];
	}

	UIActionSheet *sheet;
	
	if (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPhone)
		sheet = [[UIActionSheet alloc] initWithTitle:_("Grouping") delegate:self cancelButtonTitle:_("Cancel") destructiveButtonTitle:nil otherButtonTitles:nil];
	else
		sheet = [[UIActionSheet alloc] initWithTitle:_("Grouping") delegate:self cancelButtonTitle:nil destructiveButtonTitle:nil otherButtonTitles:nil];

	[sheet addButtonWithTitle:_("Status")];
	[sheet addButtonWithTitle:_("Priority")];
	[sheet addButtonWithTitle:_("Start date")];
	[sheet addButtonWithTitle:_("Due date")];

	if (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPhone)
		[sheet showFromToolbar:self.toolbar];
	else
	{
		[sheet showFromBarButtonItem:self.groupButton animated:YES];
		groupSheet = sheet;
	}

	[sheet release];
}

- (void)onMinuteTimer:(NSTimer *)theTimer
{
	NSFetchRequest *request = [[NSFetchRequest alloc] init];
	[request setEntity:[NSEntityDescription entityForName:@"CDTask" inManagedObjectContext:getManagedObjectContext()]];
	NSError *error;
	NSArray *tasks = [getManagedObjectContext() executeFetchRequest:request error:&error];
	[request release];
	if (tasks)
	{
		for (CDTask *task in tasks)
			[task computeDateStatus];
		
		if (![getManagedObjectContext() save:&error])
		{
			JLERROR("Could not save: %s", [[error localizedDescription] UTF8String]);
		}
	}
	else
	{
		JLERROR("Could not fetch tasks: %s", [[error localizedDescription] UTF8String]);
	}

	[self.calendarView reloadDay];
}

- (void)dealloc
{
	[self viewDidUnload];

	[tapping release];
	[currentCell release];

	[searchCell release];
	
    [super dealloc];
}

- (void)childWasPopped
{
	[self.tableView reloadData];

	if (selected)
	{
		[self.tableView selectRowAtIndexPath:selected animated:NO scrollPosition:UITableViewScrollPositionNone];
		[self.tableView deselectRowAtIndexPath:selected animated:YES];

		[selected release];
		selected = nil;
	}

	[self.calendarView reloadDay];

	if (!isCreatingTask)
		[[PositionStore instance] pop];

	isCreatingTask = NO;

	if (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPad)
	{
		[categoryController loadCategories];
		[categoryController.tableView reloadData];
	}
}

#pragma mark Fetched results controller stuff

- (void)controllerWillChangeContent:(NSFetchedResultsController *)controller
{
    [self.tableView beginUpdates];
}


- (void)controller:(NSFetchedResultsController *)controller
  didChangeSection:(id <NSFetchedResultsSectionInfo>)sectionInfo
		   atIndex:(NSUInteger)sectionIndex
	 forChangeType:(NSFetchedResultsChangeType)type
{
	sectionIndex = sectionIndex + ADJUSTSECTION;

    switch(type)
	{
        case NSFetchedResultsChangeInsert:
            [self.tableView insertSections:[NSIndexSet indexSetWithIndex:sectionIndex]
						  withRowAnimation:UITableViewRowAnimationRight];
            break;

        case NSFetchedResultsChangeDelete:
            [self.tableView deleteSections:[NSIndexSet indexSetWithIndex:sectionIndex]
						  withRowAnimation:UITableViewRowAnimationRight];
			if (selected && (selected.section == sectionIndex))
			{
				[selected release];
				selected = nil;
			}
            break;
    }
}

- (void)controller:(NSFetchedResultsController *)controller
   didChangeObject:(id)anObject
	   atIndexPath:(NSIndexPath *)indexPath
	 forChangeType:(NSFetchedResultsChangeType)type
	  newIndexPath:(NSIndexPath *)newIndexPath
{
    UITableView *tableView = self.tableView;

	indexPath = [NSIndexPath indexPathForRow:indexPath.row inSection:indexPath.section + ADJUSTSECTION];
	newIndexPath = [NSIndexPath indexPathForRow:newIndexPath.row inSection:newIndexPath.section + ADJUSTSECTION];

    switch(type)
	{
        case NSFetchedResultsChangeInsert:
            [tableView insertRowsAtIndexPaths:[NSArray arrayWithObject:newIndexPath]
							 withRowAnimation:UITableViewRowAnimationRight];
            break;
			
        case NSFetchedResultsChangeDelete:
            [tableView deleteRowsAtIndexPaths:[NSArray arrayWithObject:indexPath]
							 withRowAnimation:UITableViewRowAnimationRight];
			if (selected && ((selected.row == indexPath.row) && (selected.section == indexPath.section)))
			{
				[selected release];
				selected = nil;
			}
            break;
			
        case NSFetchedResultsChangeUpdate:
		{
			if (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPad)
			{
				TaskCelliPad *cell = (TaskCelliPad *)[tableView cellForRowAtIndexPath:indexPath];
				[cell setTask:(CDTask *)anObject target:self action:@selector(onToggleTaskCompletion:)];
			}
			else
			{
				TaskCell *cell = (TaskCell *)[tableView cellForRowAtIndexPath:indexPath];
				[cell setTask:(CDTask *)anObject target:self action:@selector(onToggleTaskCompletion:)];
			}

            break;
		}
        case NSFetchedResultsChangeMove:
            [tableView deleteRowsAtIndexPaths:[NSArray arrayWithObject:indexPath]
							 withRowAnimation:UITableViewRowAnimationRight];
            [tableView insertRowsAtIndexPaths:[NSArray arrayWithObject:newIndexPath]
							 withRowAnimation:UITableViewRowAnimationRight];
            break;
    }
}

- (void)controllerDidChangeContent:(NSFetchedResultsController *)controller
{
    [self.tableView endUpdates];
}

- (void)setEditing:(BOOL)editing animated:(BOOL)animated
{
	[self.tableViewController setEditing:editing animated:animated];
	[super setEditing:editing animated:animated];

	if (editing)
	{
		[self.tableView insertSections:[NSIndexSet indexSetWithIndex:1] withRowAnimation:UITableViewRowAnimationRight];
	}
	else
	{
		[self.tableView deleteSections:[NSIndexSet indexSetWithIndex:1] withRowAnimation:UITableViewRowAnimationRight];
	}
}

- (void)toggleTaskCompletion
{
	CDTask *task;
	
	if (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPhone)
		task = ((TaskCell *)currentCell).task;
	else
		task = ((TaskCelliPad *)currentCell).task;
	
	if (task.completionDate)
	{
		task.completionDate = nil;
	}
	else
	{
		if (task.recPeriod == nil)
			task.completionDate = [NSDate date];
		if (task.startDate)
			task.startDate = [task computeNextDate:task.startDate];
		if (task.dueDate)
			task.dueDate = [task computeNextDate:task.dueDate];
		if (task.reminderDate)
			task.reminderDate = [task computeNextDate:task.reminderDate];
	}

	[task computeDateStatus];
	[task markDirty];
	[task save];

	[currentCell release];
	currentCell = nil;
}

- (void)onToggleTaskCompletion:(UITableViewCell *)cell
{
	currentCell = [cell retain];
	CDTask *task;
	
	if (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPhone)
		task = ((TaskCell *)currentCell).task;
	else
		task = ((TaskCelliPad *)currentCell).task;
	
	tapping = [[self.tableView indexPathForCell:cell] retain];

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
	return [[results sections] count] + ADJUSTSECTION;
}

- (NSString *)tableView:(UITableView *)tableView titleForHeaderInSection:(NSInteger)section
{
	if (self.editing && (section <= 1))
		return @"";

	if (section == 0)
		return @"";

	if ([Configuration configuration].taskGrouping == GROUP_STATUS)
	{
		switch ([[[[results sections] objectAtIndex:section - ADJUSTSECTION] name] integerValue])
		{
			case TASKSTATUS_OVERDUE:
				return _("Overdue");
			case TASKSTATUS_DUESOON:
				return _("Due soon");
			case TASKSTATUS_STARTED:
				return _("Started");
			case TASKSTATUS_NOTSTARTED:
				return _("Not started");
			case TASKSTATUS_COMPLETED:
				return _("Completed");
		}
	}

	return [[[results sections] objectAtIndex:section - ADJUSTSECTION] name];
}

- (CGFloat)tableView:(UITableView *)tableView heightForHeaderInSection:(NSInteger)section
{
	return (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPad) ? 48 : 26;
}

- (UIView *)tableView:(UITableView *)tableView viewForHeaderInSection:(NSInteger)section
{
	if (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPad)
	{
		if (self.editing && (section <= 1))
			return nil;
		
		if (section == 0)
			return nil;

		[[NSBundle mainBundle] loadNibNamed:@"PaperHeaderView" owner:self options:nil];
		headerView.label.text = [self tableView:tableView titleForHeaderInSection:section];
		
		// XXXFIXME: there may be a leak here. I don't quite understand who releases this
		// object.

		return [headerView retain];
	}

	return nil;
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section
{
	if (section == 0)
		return 1; // Search cell
	
	if (self.editing && (section == 1))
		return 1; // Add task cell

	if ([[results sections] count])
	{
		NSLog(@"%d objects for section %d", [[[results sections] objectAtIndex:section - ADJUSTSECTION] numberOfObjects], section);
		return [[[results sections] objectAtIndex:section - ADJUSTSECTION] numberOfObjects];
	}

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

		cell.textLabel.text = _("Add task...");
	}
	else if (indexPath.section == 0)
	{
		return searchCell;
	}
	else
	{
		if (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPhone)
		{
			TaskCell *taskCell = (TaskCell *)[tableView dequeueReusableCellWithIdentifier:@"TaskCell"];
			
			if (taskCell == nil)
			{
				taskCell = [[[CellFactory cellFactory] createTaskCell] autorelease];
			}
			
			// This is already done in the NIB but when switching to non-editing mode, we
			// must enforce it...
			taskCell.accessoryType = UITableViewCellAccessoryDisclosureIndicator;
			
			CDTask *task = [results objectAtIndexPath:[NSIndexPath indexPathForRow:indexPath.row inSection:indexPath.section - ADJUSTSECTION]];
			[taskCell setTask:task target:self action:@selector(onToggleTaskCompletion:)];
			
			cell = (UITableViewCell *)taskCell;
		}
		else
		{
			// Don't dequeue here, it causes trouble with variable-height cells
			TaskCelliPad *taskCell = [[[CellFactory cellFactory] createTaskCelliPad] autorelease];

			CDTask *task = [results objectAtIndexPath:[NSIndexPath indexPathForRow:indexPath.row inSection:indexPath.section - ADJUSTSECTION]];
			[taskCell setTask:task target:self action:@selector(onToggleTaskCompletion:)];
			
			cell = (UITableViewCell *)taskCell;
			cell.editingAccessoryType = UITableViewCellAccessoryDetailDisclosureButton;
		}
	}

    return cell;
}

- (CGFloat)tableView:(UITableView *)tableView heightForRowAtIndexPath:(NSIndexPath *)indexPath
{
	if (indexPath.section == 0)
		return 44;

	if (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPad)
	{
		if (self.editing && (indexPath.section == 1))
		{
			return 60;
		}

		return [Configuration configuration].compactTasks ? 61 : 161;
	}
	else
		return [Configuration configuration].compactTasks ? 44 : 60;
}

- (UITableViewCellEditingStyle)tableView:(UITableView *)tableView editingStyleForRowAtIndexPath:(NSIndexPath *)indexPath
{
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
		[self onAddTask:nil];
		return;
	}
	else
	{
		CDTask *task = [results objectAtIndexPath:[NSIndexPath indexPathForRow:indexPath.row inSection:indexPath.section - ADJUSTSECTION]];
		deleteTask(task);
		[task save];
	}
}

- (IBAction)onAddTask:(UIBarButtonItem *)button
{
	isCreatingTask = YES;

	if (groupSheet)
	{
		[groupSheet dismissWithClickedButtonIndex:-1 animated:YES];
		groupSheet = nil;
	}

	if (popCtrl)
	{
		[popCtrl dismissPopoverAnimated:YES];
	}
}

- (IBAction)onSync:(UIBarButtonItem *)button
{
	[categoryController setWantSync];

	[self.navigationController popToRootViewControllerAnimated:YES];
}

- (IBAction)onSwitch:(UIBarButtonItem *)button
{
	if (groupSheet)
		[groupSheet dismissWithClickedButtonIndex:-1 animated:YES];
	
	if (popCtrl)
		[popCtrl dismissPopoverAnimated:YES];

	[UIView beginAnimations:@"SwitchStyleAnimation" context:nil];
	[UIView setAnimationDuration:1.0];

	if (self.tableView.hidden)
	{
		[UIView setAnimationTransition:UIViewAnimationTransitionFlipFromLeft forView:self.view cache:YES];
		// Switch to table view
		self.tableView.hidden = NO;
		self.calendarView.hidden = YES;
		self.calendarSearch.hidden = YES;
		[UIView commitAnimations];
		self.navigationItem.rightBarButtonItem = [self editButtonItem];
		
		NSMutableArray *items = [NSMutableArray arrayWithArray:self.toolbar.items];
		UIBarButtonItem *btn = [[UIBarButtonItem alloc] initWithImage:[UIImage imageNamed:@"switchcal.png"] style:UIBarButtonItemStyleBordered target:self action:@selector(onSwitch:)];
		btn.tag = 1;
		[items replaceObjectAtIndex:[self calendarButtonIndex] withObject:btn];
		[btn release];
		[self.toolbar setItems:items animated:NO];

		for (NSInteger i = 1; i < [self.navigationController.viewControllers count] - 1; ++i)
		{
			TaskViewController *ctrl = [self.navigationController.viewControllers objectAtIndex:i];
			ctrl.tableView.hidden = NO;
			ctrl.calendarView.hidden = YES;
			ctrl.calendarSearch.hidden = YES;
			ctrl.navigationItem.rightBarButtonItem = [ctrl editButtonItem];
			
			NSMutableArray *items = [NSMutableArray arrayWithArray:ctrl.toolbar.items];
			btn = [[UIBarButtonItem alloc] initWithImage:[UIImage imageNamed:@"switchcal.png"] style:UIBarButtonItemStyleBordered target:ctrl action:@selector(onSwitch:)];
			btn.tag = 1;
			[items replaceObjectAtIndex:[ctrl calendarButtonIndex] withObject:btn];
			[btn release];
			[ctrl.toolbar setItems:items animated:NO];
		}

		[Configuration configuration].viewStyle = STYLE_TABLE;
		[[Configuration configuration] save];
	}
	else
	{
		[UIView setAnimationTransition:UIViewAnimationTransitionFlipFromRight forView:self.view cache:YES];
		// Switch to calendar view
		self.tableView.hidden = YES;
		self.calendarView.hidden = NO;
		self.calendarSearch.hidden = NO;
		[UIView commitAnimations];
		self.navigationItem.rightBarButtonItem = nil;
		
		NSMutableArray *items = [NSMutableArray arrayWithArray:self.toolbar.items];
		UIBarButtonItem *btn = [[UIBarButtonItem alloc] initWithImage:[UIImage imageNamed:@"switchtable.png"] style:UIBarButtonItemStyleBordered target:self action:@selector(onSwitch:)];
		btn.tag = 1;
		[items replaceObjectAtIndex:[self calendarButtonIndex] withObject:btn];
		[btn release];
		[self.toolbar setItems:items animated:NO];

		for (NSInteger i = 1; i < [self.navigationController.viewControllers count] - 1; ++i)
		{
			TaskViewController *ctrl = [self.navigationController.viewControllers objectAtIndex:i];
			ctrl.tableView.hidden = YES;
			ctrl.calendarView.hidden = NO;
			ctrl.calendarSearch.hidden = NO;
			ctrl.navigationItem.rightBarButtonItem = nil;
			
			NSMutableArray *items = [NSMutableArray arrayWithArray:ctrl.toolbar.items];
			btn = [[UIBarButtonItem alloc] initWithImage:[UIImage imageNamed:@"switchtable.png"] style:UIBarButtonItemStyleBordered target:ctrl action:@selector(onSwitch:)];
			btn.tag = 1;
			[items replaceObjectAtIndex:[ctrl calendarButtonIndex] withObject:btn];
			[btn release];
			[ctrl.toolbar setItems:items animated:NO];
		}
		
		[Configuration configuration].viewStyle = STYLE_CALENDAR;
		[[Configuration configuration] save];
	}
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
	
	selected = [indexPath retain];

	if ((self.editing && indexPath.section == 1) || (!self.editing && (indexPath.section == 0)))
	{
		[self onAddTask:nil];
		return;
	}

	CDTask *task = [results objectAtIndexPath:[NSIndexPath indexPathForRow:indexPath.row inSection:indexPath.section - ADJUSTSECTION]];
	UIViewController *ctrl;

	if (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPad)
	{
		ctrl = [[TaskDetailsControlleriPad alloc] initWithTask:task];
	}
	else
	{
		ctrl = [[TaskDetailsController alloc] initWithTask:task];
	}

	[self.navigationController pushViewController:ctrl animated:YES];

	[[PositionStore instance] push:self indexPath:[NSIndexPath indexPathForRow:indexPath.row inSection:(indexPath.section - ADJUSTSECTION)] type:TYPE_DETAILS searchWord:searchCell.searchBar.text];
	[ctrl release];
}

- (void)tableView:(UITableView *)tableView accessoryButtonTappedForRowWithIndexPath:(NSIndexPath *)indexPath
{
	CDTask *task = [results objectAtIndexPath:[NSIndexPath indexPathForRow:indexPath.row inSection:indexPath.section - ADJUSTSECTION]];
	ParentTaskViewController *ctrl = [[ParentTaskViewController alloc] initWithCategoryController:categoryController edit:self.editing parent:task];
	[[PositionStore instance] push:self indexPath:[NSIndexPath indexPathForRow:indexPath.row inSection:(indexPath.section - ADJUSTSECTION)] type:TYPE_SUBTASK searchWord:searchCell.searchBar.text];
	[self.navigationController pushViewController:ctrl animated:YES];
	[ctrl release];
}

#pragma mark UISearchBarDelegate

- (void)searchBarSearchButtonClicked:(UISearchBar *)searchBar
{
	[searchBar resignFirstResponder];
	
	searchCell.searchBar.text = searchBar.text;
	calendarSearch.text = searchBar.text;
	
	[self populate];
	[self.tableView reloadData];
	[self.calendarView reloadDay];
}

- (void)searchBarCancelButtonClicked:(UISearchBar *)searchBar
{
	searchCell.searchBar.text = @"";
	calendarSearch.text = @"";
	
	[searchBar resignFirstResponder];

	[self populate];
	[self.tableView reloadData];
	[self.calendarView reloadDay];
}

// Calendar delegate

- (NSArray *)calendarDayTimelineView:(ODCalendarDayTimelineView*)calendarDayTimeline eventsForDate:(NSDate *)eventDate
{
	NSMutableArray *events = [[NSMutableArray alloc] init];
	
	for (CDTask *task in results.fetchedObjects)
	{
		if (!(task.startDate && task.dueDate))
			continue;
		if (![Configuration configuration].showCompleted && task.completionDate)
			continue;
		if (![Configuration configuration].showInactive && ([task.dateStatus intValue] == TASKSTATUS_NOTSTARTED))
			continue;
		
		if ([task.startDate compare:[[NSDate midnightToday] addTimeInterval:24*60*60]] == NSOrderedDescending)
			continue;
		if ([task.dueDate compare:[NSDate midnightToday]] == NSOrderedAscending)
			continue;
		
		CalendarTaskView *event = [[CalendarTaskView alloc] initWithTask:task];
		[events addObject:event];
		[event release];
	}
	
	return [events autorelease];
}

- (void)calendarDayTimelineView:(ODCalendarDayTimelineView*)calendarDayTimeline eventViewWasSelected:(ODCalendarDayEventView *)eventView atPoint:(CGPoint)point
{
	CDTask *task = ((CalendarTaskView *)eventView).task;
	NSIndexPath *indexPath = [results indexPathForObject:task];

	if ([[task children] count])
	{
		if ((point.x >= eventView.bounds.size.width - 36) && (point.y >= eventView.bounds.size.height - 36))
		{
			ParentTaskViewController *ctrl = [[ParentTaskViewController alloc] initWithCategoryController:categoryController edit:self.editing parent:task];
			[[PositionStore instance] push:self indexPath:indexPath type:TYPE_SUBTASK searchWord:searchCell.searchBar.text];
			[self.navigationController pushViewController:ctrl animated:YES];
			[ctrl release];
			
			return;
		}
	}

	UIViewController *ctrl;
	if (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPhone)
		ctrl = [[TaskDetailsController alloc] initWithTask:task];
	else
		ctrl = [[TaskDetailsControlleriPad alloc] initWithTask:task];

	[self.navigationController pushViewController:ctrl animated:YES];
	[[PositionStore instance] push:self indexPath:indexPath type:TYPE_DETAILS searchWord:searchCell.searchBar.text];
	[ctrl release];
}

- (NSInteger)calendarDayTimelineViewStartHour:(ODCalendarDayTimelineView*)calendarDayTimeline
{
	if ([Configuration configuration].cdCurrentFile)
		return [[Configuration configuration].cdCurrentFile.startHour intValue];
	return 8;
}

- (NSInteger)calendarDayTimelineViewEndHour:(ODCalendarDayTimelineView*)calendarDayTimeline
{
	if ([Configuration configuration].cdCurrentFile)
		return [[Configuration configuration].cdCurrentFile.endHour intValue];
	return 18;
}

#pragma mark UIActionSheetDelegate

- (void)actionSheet:(UIActionSheet *)actionSheet didDismissWithButtonIndex:(NSInteger)buttonIndex
{
	NSInteger selection;

	if (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPad)
	{
		groupSheet = nil;

		if (buttonIndex < 0)
			return;
		selection = buttonIndex;
	}
	else
	{
		if (buttonIndex <= 0)
			return;
		selection = buttonIndex - 1;
	}

	if (selection == [Configuration configuration].taskGrouping)
	{
		[Configuration configuration].reverseGrouping = ![Configuration configuration].reverseGrouping;
	}
	else
	{
		[Configuration configuration].taskGrouping = selection;
		[Configuration configuration].reverseGrouping = NO;
	}

	[[Configuration configuration] save];
	[self populate];
	[self.tableView reloadData];
}

@end

