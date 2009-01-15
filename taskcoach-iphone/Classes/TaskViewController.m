//
//  TaskViewController.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 15/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import "TaskViewController.h"

#import "TaskList.h"

@implementation TaskViewController

- initWithTitle:(NSString *)theTitle category:(NSInteger)categoryId
{
	if (self = [super initWithNibName:@"TaskView" bundle:[NSBundle mainBundle]])
	{
		title = [theTitle retain];
		
		overdueList = [[TaskList alloc] initWithView:@"OverdueTask" category:categoryId];
		dueTodayList = [[TaskList alloc] initWithView:@"DueTodayTask" category:categoryId];
		startedList = [[TaskList alloc] initWithView:@"StartedTask" category:categoryId];
		notStartedList = [[TaskList alloc] initWithView:@"NotStartedTask" category:categoryId];
	}
	
	return self;
}

- (void)viewDidLoad
{
	self.navigationItem.title = title;
}

- (void)dealloc
{
	[title release];
	[overdueList release];
	[dueTodayList release];
	[startedList release];
	[notStartedList release];

    [super dealloc];
}

#pragma mark Table view methods

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView
{
    return 4;
}

- (NSString *)tableView:(UITableView *)tableView titleForHeaderInSection:(NSInteger)section
{
	switch (section)
	{
		case 0:
			return NSLocalizedString(@"Overdue", @"Overdue tasks header title");
		case 1:
			return NSLocalizedString(@"Due today", @"Due today tasks header title");
		case 2:
			return NSLocalizedString(@"Started", @"Started tasks header title");
		case 3:
			return NSLocalizedString(@"Not started", @"Not started tasks header title");
	}
	
	return NSLocalizedString(@"Others", @"Other tasks header title; should not exist...");
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section
{
	switch (section)
	{
		case 0:
			return [overdueList count];
		case 1:
			return [dueTodayList count];
		case 2:
			return [startedList count];
		case 3:
			return [notStartedList count];
		default:
			return 0;
	}
}

- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath
{
    static NSString *CellIdentifier = @"Cell";
    
    UITableViewCell *cell = [tableView dequeueReusableCellWithIdentifier:CellIdentifier];
    if (cell == nil)
	{
        cell = [[[UITableViewCell alloc] initWithFrame:CGRectZero reuseIdentifier:CellIdentifier] autorelease];
    }

	switch (indexPath.section)
	{
		case 0:
			cell.text = [[overdueList taskAtIndex:indexPath.row] name];
			break;
		case 1:
			cell.text = [[dueTodayList taskAtIndex:indexPath.row] name];
			break;
		case 2:
			cell.text = [[startedList taskAtIndex:indexPath.row] name];
			break;
		case 3:
			cell.text = [[notStartedList taskAtIndex:indexPath.row] name];
			break;
		default:
			cell.text = @"Testing";
			break;
	}

    return cell;
}

@end

