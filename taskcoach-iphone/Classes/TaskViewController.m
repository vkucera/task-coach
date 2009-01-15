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
		
		TaskList *list;
		headers = [[NSMutableArray alloc] initWithCapacity:4];
		
		list = [[TaskList alloc] initWithView:@"OverdueTask" category:categoryId title:NSLocalizedString(@"Overdue", @"Overdue task title")];
		if ([list count])
		{
			[headers addObject:list];
		}
		[list release];

		list = [[TaskList alloc] initWithView:@"DueTodayTask" category:categoryId title:NSLocalizedString(@"Due today", @"Due today task title")];
		if ([list count])
		{
			[headers addObject:list];
		}
		[list release];

		list = [[TaskList alloc] initWithView:@"StartedTask" category:categoryId title:NSLocalizedString(@"Started", @"Started task title")];
		if ([list count])
		{
			[headers addObject:list];
		}
		[list release];

		list = [[TaskList alloc] initWithView:@"NotStartedTask" category:categoryId title:NSLocalizedString(@"Not started", @"Not started task title")];
		if ([list count])
		{
			[headers addObject:list];
		}
		[list release];
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
	[headers release];

    [super dealloc];
}

#pragma mark Table view methods

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView
{
	NSInteger count = [headers count];

    return count ? count : 1;
}

- (NSString *)tableView:(UITableView *)tableView titleForHeaderInSection:(NSInteger)section
{
	if ([headers count])
	{
		return [[headers objectAtIndex:section] title];
	}
	
	return NSLocalizedString(@"No tasks.", @"No tasks header");
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section
{
	if ([headers count])
	{
		return [[headers objectAtIndex:section] count];
	}
	
	return 0;
}

- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath
{
    static NSString *CellIdentifier = @"Cell";
    
    UITableViewCell *cell = [tableView dequeueReusableCellWithIdentifier:CellIdentifier];
    if (cell == nil)
	{
        cell = [[[UITableViewCell alloc] initWithFrame:CGRectZero reuseIdentifier:CellIdentifier] autorelease];
    }

	cell.text = [[[headers objectAtIndex:indexPath.section] taskAtIndex:indexPath.row] name];

    return cell;
}

@end

