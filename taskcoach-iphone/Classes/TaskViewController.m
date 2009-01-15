//
//  TaskViewController.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 15/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import "TaskViewController.h"

@implementation TaskViewController

- initWithTitle:(NSString *)theTitle
{
	if (self = [super initWithNibName:@"TaskView" bundle:[NSBundle mainBundle]])
	{
		title = [theTitle retain];
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
    return 10;
}

- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath
{
    static NSString *CellIdentifier = @"Cell";
    
    UITableViewCell *cell = [tableView dequeueReusableCellWithIdentifier:CellIdentifier];
    if (cell == nil)
	{
        cell = [[[UITableViewCell alloc] initWithFrame:CGRectZero reuseIdentifier:CellIdentifier] autorelease];
    }

    cell.text = @"Testing...";

    return cell;
}

@end

