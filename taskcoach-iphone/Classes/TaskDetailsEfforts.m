//
//  TaskDetailsEfforts.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 16/05/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import "TaskCoachAppDelegate.h"
#import "TaskDetailsEfforts.h"
#import "CellFactory.h"
#import "CDDomainObject+Addons.h"
#import "CDEffort.h"
#import "CDEffort+Addons.h"
#import "CDTask.h"
#import "CDTask+Addons.h"
#import "String+Utils.h"
#import "i18n.h"

@interface TaskDetailsEfforts ()

- (void)updateTrackButton;

@end;

@implementation TaskDetailsEfforts

- initWithTask:(CDTask *)theTask
{
	if (self = [super initWithNibName:@"TaskDetailsEfforts" bundle:[NSBundle mainBundle]])
	{
		task = [theTask retain];
		
		effortCell = [[[CellFactory cellFactory] createButtonCell] retain];
		[effortCell.button setTitleColor:[UIColor blackColor] forState:UIControlStateNormal];
		[effortCell setTarget:self action:@selector(onTrack:)];
	}

	return self;
}

- (void)viewDidLoad
{
	[super viewDidLoad];

	[self updateTrackButton];

	NSFetchRequest *request = [[NSFetchRequest alloc] init];
	[request setEntity:[NSEntityDescription entityForName:@"CDEffort" inManagedObjectContext:getManagedObjectContext()]];
	[request setPredicate:[NSPredicate predicateWithFormat:@"status != %d AND task=%@", STATUS_DELETED, task]];

	NSSortDescriptor *sd = [[NSSortDescriptor alloc] initWithKey:@"started" ascending:NO];
	[request setSortDescriptors:[NSArray arrayWithObject:sd]];
	[sd release];
	
	results = [[NSFetchedResultsController alloc] initWithFetchRequest:request managedObjectContext:getManagedObjectContext() sectionNameKeyPath:nil cacheName:@"CDEffortCache"];
	results.delegate = self;

	NSError *error;
	if (![results performFetch:&error])
	{
		NSLog(@"Error fetching efforts: %@", [error localizedDescription]);

		UIAlertView *alert = [[UIAlertView alloc] initWithTitle:_("Error") message:_("Could not fetch efforts") delegate:self cancelButtonTitle:_("OK") otherButtonTitles:nil];
		[alert show];
		[alert release];
	}
}

- (void)viewDidUnload
{
	[results release];
	results = nil;
}

- (void)dealloc
{
	[self viewDidUnload];

	[task release];
	[effortCell release];
	[super dealloc];
}

- (void)onTrack:(ButtonCell *)cell
{
	if ([task currentEffort])
	{
		[task stopTracking];
		[self updateTrackButton];
		[self.tableView reloadRowsAtIndexPaths:[NSArray arrayWithObject:[NSIndexPath indexPathForRow:0 inSection:1]] withRowAnimation:UITableViewRowAnimationFade];
	}
	else
	{
		NSInteger count = [[CDEffort currentEfforts] count];
		if (count)
		{
			UIAlertView *alert = [[UIAlertView alloc] initWithTitle:_("Warning") message:[NSString stringWithFormat:_("There are %d task(s) currently tracked. Stop tracking them ?"), count]
														   delegate:self cancelButtonTitle:_("Cancel") otherButtonTitles:_("Yes"), _("No"), nil];
			[alert show];
			[alert release];
		}
		else
		{
			[task startTracking];
			
			NSError *error;
			if (![getManagedObjectContext() save:&error])
			{
				NSLog(@"Could not save efforts: %@", [error localizedDescription]);
				UIAlertView *alert = [[UIAlertView alloc] initWithTitle:_("Error") message:_("Error saving effort") delegate:self cancelButtonTitle:_("OK") otherButtonTitles:nil];
				[alert show];
				[alert release];
			}

			[self updateTrackButton];
		}
	}
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)toInterfaceOrientation
{
	return YES;
}

- (void)updateTrackButton
{
	BOOL isTracking = [task currentEffort] != nil;
	
	UIImage *img;
	
	if (isTracking)
	{
		img = [[UIImage imageNamed:@"blueButton.png"] stretchableImageWithLeftCapWidth:12.0 topCapHeight:0.0];
	}
	else
	{
		img = [[UIImage imageNamed:@"redButton.png"] stretchableImageWithLeftCapWidth:12.0 topCapHeight:0.0];
	}
	
	[effortCell.button setBackgroundImage:img forState:UIControlStateNormal];
	
	img = [[UIImage imageNamed:@"whiteButton.png"] stretchableImageWithLeftCapWidth:12.0 topCapHeight:0.0];
	[effortCell.button setBackgroundImage:img forState:UIControlStateHighlighted];
	
	if (isTracking)
		[effortCell.button setTitle:_("Stop tracking") forState:UIControlStateNormal];
	else
		[effortCell.button setTitle:_("Start tracking") forState:UIControlStateNormal];
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
	sectionIndex++;
	
    switch(type)
	{
        case NSFetchedResultsChangeInsert:
            [self.tableView insertSections:[NSIndexSet indexSetWithIndex:sectionIndex]
						  withRowAnimation:UITableViewRowAnimationRight];
            break;
			
        case NSFetchedResultsChangeDelete:
            [self.tableView deleteSections:[NSIndexSet indexSetWithIndex:sectionIndex]
						  withRowAnimation:UITableViewRowAnimationRight];
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
	
	indexPath = [NSIndexPath indexPathForRow:indexPath.row inSection:indexPath.section + 1];
	newIndexPath = [NSIndexPath indexPathForRow:newIndexPath.row inSection:newIndexPath.section + 1];
	
    switch(type)
	{
        case NSFetchedResultsChangeInsert:
            [tableView insertRowsAtIndexPaths:[NSArray arrayWithObject:newIndexPath]
							 withRowAnimation:UITableViewRowAnimationRight];
            break;
			
        case NSFetchedResultsChangeDelete:
            [tableView deleteRowsAtIndexPaths:[NSArray arrayWithObject:indexPath]
							 withRowAnimation:UITableViewRowAnimationRight];
            break;
			
        case NSFetchedResultsChangeUpdate:
			// XXXTODO
			// [((TaskCell *)[tableView cellForRowAtIndexPath:indexPath]) setTask:(CDTask *)anObject target:self action:@selector(onToggleTaskCompletion:)];
            break;
			
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

#pragma mark UIAlertViewDelegate methods

- (void)alertView:(UIAlertView *)alertView didDismissWithButtonIndex:(NSInteger)buttonIndex
{
	switch (buttonIndex)
	{
		case 0: // Cancel
			break;
		case 1: // Yes: stop tracking other tasks
		{
			NSDate *now = [NSDate date];
			
			for (CDEffort *effort in [CDEffort currentEfforts])
			{
				effort.ended = now;
				[effort markDirty];
			}

			NSError *error;
			if (![getManagedObjectContext() save:&error])
			{
				UIAlertView *alert = [[UIAlertView alloc] initWithTitle:_("Error") message:_("Could not save efforts") delegate:self cancelButtonTitle:_("OK") otherButtonTitles:nil];
				[alert show];
				[alert release];
			}
		}
			// No break; intended
		case 2: // No, don't stop tracking others
			[task startTracking];
			
			NSError *error;
			if (![getManagedObjectContext() save:&error])
			{
				NSLog(@"Could not save efforts: %@", [error localizedDescription]);
				UIAlertView *alert = [[UIAlertView alloc] initWithTitle:_("Error") message:_("Error saving effort") delegate:self cancelButtonTitle:_("OK") otherButtonTitles:nil];
				[alert show];
				[alert release];
			}

			[self updateTrackButton];
			break;
	}
}

#pragma mark Table view methods

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView
{
    return [[results sections] count] + 1;
}

- (NSString *)tableView:(UITableView *)tableView titleForHeaderInSection:(NSInteger)section
{
	switch (section)
	{
		case 0:
		{
			// XXXTODO
			/*
			if (effortCount)
				return [NSString stringWithFormat:_("%d effort(s)"), effortCount];
			else
				return _("No effort.");
			 */
			break;
		}
		default:
		{
			return [[[results sections] objectAtIndex:section - 1] name];
		}
	}

	return nil;
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section
{
	switch (section)
	{
		case 0:
			return 1;
		default:
			return [[[results sections] objectAtIndex:section - 1] numberOfObjects];
	}

	return 0;
}

- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath
{
    if (indexPath.section == 0)
	{
		return effortCell;
	}
	else
	{
		static NSString *CellIdentifier = @"Cell";
		
		UITableViewCell *cell = [tableView dequeueReusableCellWithIdentifier:CellIdentifier];
		if (cell == nil)
		{
			cell = [[[UITableViewCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:CellIdentifier] autorelease];
		}
		
		CDEffort *effort = [results objectAtIndexPath:[NSIndexPath indexPathForRow:indexPath.row inSection:indexPath.section - 1]];
		
		if (effort.ended)
		{
			NSTimeInterval duration = [effort.ended timeIntervalSinceDate:effort.started];
			cell.textLabel.text = [NSString formatTimeInterval:(NSInteger)duration];
		}
		else
		{
			cell.textLabel.text = [NSString stringWithFormat:_("Started %@"), effort.started];
		}
		
		cell.selectionStyle = UITableViewCellSelectionStyleNone;
		
		return cell;
	}
}

@end

