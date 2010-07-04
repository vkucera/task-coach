//
//  TaskDetailsEfforts.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 16/05/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import "TaskDetailsEfforts.h"
#import "CellFactory.h"
#import "CDTask+Addons.h"

@implementation TaskDetailsEfforts

- initWithTask:(CDTask *)theTask
{
	if ((self = [super initWithTask:theTask]))
	{
		effortCell = [[[CellFactory cellFactory] createButtonCell] retain];
		[effortCell.button setTitleColor:[UIColor blackColor] forState:UIControlStateNormal];
		[effortCell setTarget:self action:@selector(onClickTrack:)];
	}

	return self;
}

- (void)viewDidLoad
{
	[super viewDidLoad];

	[self updateButton:effortCell.button];
}

- (void)dealloc
{
	[effortCell release];

	[super dealloc];
}

- (void)refreshTotal
{
	[super refreshTotal];

	[self.tableView reloadRowsAtIndexPaths:[NSArray arrayWithObject:[NSIndexPath indexPathForRow:0 inSection:1]] withRowAnimation:UITableViewRowAnimationNone];
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)toInterfaceOrientation
{
	return YES;
}

- (void)onClickTrack:(ButtonCell *)cell
{
	[self onTrack:cell.button];
}

- (void)updateButton:(UIButton *)button
{
	[super updateButton:button];
}

- (void)controller:(NSFetchedResultsController *)controller
  didChangeSection:(id <NSFetchedResultsSectionInfo>)sectionInfo
		   atIndex:(NSUInteger)sectionIndex
	 forChangeType:(NSFetchedResultsChangeType)type
{
	[super controller:controller didChangeSection:sectionInfo atIndex:sectionIndex + 1 forChangeType:type];
}
- (void)controller:(NSFetchedResultsController *)controller
   didChangeObject:(id)anObject
	   atIndexPath:(NSIndexPath *)indexPath
	 forChangeType:(NSFetchedResultsChangeType)type
	  newIndexPath:(NSIndexPath *)newIndexPath
{
	[super controller:controller didChangeObject:anObject atIndexPath:[NSIndexPath indexPathForRow:indexPath.row inSection:indexPath.section + 1]
		forChangeType:type newIndexPath:[NSIndexPath indexPathForRow:newIndexPath.row inSection:newIndexPath.section + 1]];
}

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView
{
	return [super numberOfSectionsInTableView:tableView] + 1;
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section
{
	switch (section)
	{
		case 0:
			return 1;
	}
	
	return [super tableView:tableView numberOfRowsInSection:section - 1];
}

- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath
{
	switch (indexPath.section)
	{
		case 0:
			return effortCell;
	}

	return [super tableView:tableView cellForRowAtIndexPath:[NSIndexPath indexPathForRow:indexPath.row inSection:indexPath.section - 1]];
}

@end

