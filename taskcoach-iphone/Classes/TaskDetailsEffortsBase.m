//
//  TaskDetailsEffortsBase.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 19/06/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import "TaskCoachAppDelegate.h"
#import "TaskDetailsEffortsBase.h"
#import "CDTask.h"
#import "CDTask+Addons.h"
#import "CDDomainObject+Addons.h"
#import "CDEffort.h"
#import "CDEffort+Addons.h"
#import "String+Utils.h"
#import "DateUtils.h"
#import "i18n.h"

@interface TaskDetailsEffortsBase ()

- (void)populate;

@end

@implementation TaskDetailsEffortsBase

#pragma mark -
#pragma mark Initialization

- initWithTask:(CDTask *)theTask
{
	if ((self = [super initWithNibName:@"TaskDetailsEffortsBase" bundle:[NSBundle mainBundle]]))
	{
		task = [theTask retain];
	}

	return self;
}

- (void)setTask:(CDTask *)theTask
{
	[task release];
	task = [theTask retain];

	[self populate];
	[self.tableView reloadData]; // XXXFIXME: maybe not mandatory
}

- (void)populate
{
	[results release];

	[self refreshTotal];

	NSFetchRequest *request = [[NSFetchRequest alloc] init];
	[request setEntity:[NSEntityDescription entityForName:@"CDEffort" inManagedObjectContext:getManagedObjectContext()]];
	[request setPredicate:[NSPredicate predicateWithFormat:@"status != %d AND task=%@", STATUS_DELETED, task]];
	
	NSSortDescriptor *sd = [[NSSortDescriptor alloc] initWithKey:@"started" ascending:NO];
	[request setSortDescriptors:[NSArray arrayWithObject:sd]];
	[sd release];

	results = [[NSFetchedResultsController alloc] initWithFetchRequest:request managedObjectContext:getManagedObjectContext() sectionNameKeyPath:nil cacheName:nil];
	results.delegate = self;
	
	NSError *error;
	if (![results performFetch:&error])
	{
		NSLog(@"Error fetching efforts: %@", [error localizedDescription]);
		
		UIAlertView *alert = [[UIAlertView alloc] initWithTitle:@"Error" message:@"Could not fetch efforts" delegate:self cancelButtonTitle:@"OK" otherButtonTitles:nil];
		[alert show];
		[alert release];
	}

	[request release];
}

#pragma mark -
#pragma mark View lifecycle

- (void)viewDidLoad
{
	[super viewDidLoad];
	[self populate];

	updater = [NSTimer scheduledTimerWithTimeInterval:1 target:self selector:@selector(onUpdateTotal:) userInfo:nil repeats:YES];
}

- (void)viewDidUnload
{
	[results release];
	results = nil;

	[updater invalidate];
	updater = nil;
}

- (void)dealloc
{
	[self viewDidUnload];

	[task release];

	[super dealloc];
}

#pragma mark Actions

- (void)onUpdateTotal:(NSTimer *)timer
{
	[self refreshTotal];
}

- (void)updateButton:(UIButton *)button
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
	
	[button setBackgroundImage:img forState:UIControlStateNormal];
	
	img = [[UIImage imageNamed:@"whiteButton.png"] stretchableImageWithLeftCapWidth:12.0 topCapHeight:0.0];
	[button setBackgroundImage:img forState:UIControlStateHighlighted];
	
	if (isTracking)
		[button setTitle:_("Stop tracking") forState:UIControlStateNormal];
	else
	{
		[button setTitle:_("Start tracking") forState:UIControlStateNormal];
		[self refreshTotal];
	}
}

- (void)onTrack:(UIButton *)button
{
	if ([task currentEffort])
	{
		[task stopTracking];
		[task save];
		[self updateButton:button];
	}
	else
	{
		NSInteger count = [[CDEffort currentEfforts] count];
		if (count)
		{
			myButton = button;
			UIAlertView *alert = [[UIAlertView alloc] initWithTitle:_("Warning") message:[NSString stringWithFormat:_("There are %d task(s) currently tracked. Stop tracking them ?"), count]
														   delegate:self cancelButtonTitle:_("Cancel") otherButtonTitles:_("Yes"), _("No"), nil];
			[alert show];
			[alert release];
		}
		else
		{
			[task startTracking];
			[task save];
			
			[self updateButton:button];
		}
	}
}

- (void)refreshTotal
{
	NSFetchRequest *request = [[NSFetchRequest alloc] init];
	[request setEntity:[NSEntityDescription entityForName:@"CDEffort" inManagedObjectContext:getManagedObjectContext()]];
	[request setPredicate:[NSPredicate predicateWithFormat:@"status != %d AND task=%@", STATUS_DELETED, task]];
	NSError *error;
	NSArray *efforts = [getManagedObjectContext() executeFetchRequest:request error:&error];
	[request release];

	if (efforts)
	{
		totalSpent = 0;

		for (CDEffort *effort in efforts)
		{
			if (effort.ended)
				totalSpent += [effort.ended timeIntervalSinceDate:effort.started];
			else
				totalSpent += [[NSDate date] timeIntervalSinceDate:effort.started];
		}
	}

	[self.tableView reloadRowsAtIndexPaths:[NSArray arrayWithObject:[NSIndexPath indexPathForRow:0 inSection:0]] withRowAnimation:UITableViewRowAnimationNone];
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
    switch(type)
	{
        case NSFetchedResultsChangeInsert:
            [self.tableView insertSections:[NSIndexSet indexSetWithIndex:sectionIndex + 1]
						  withRowAnimation:UITableViewRowAnimationRight];
            break;
			
        case NSFetchedResultsChangeDelete:
            [self.tableView deleteSections:[NSIndexSet indexSetWithIndex:sectionIndex + 1]
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
			[tableView reloadRowsAtIndexPaths:[NSArray arrayWithObject:newIndexPath] withRowAnimation:UITableViewRowAnimationFade];
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
		case -1: // iPad touch outside
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
		}
			// No break; intended
		case 2: // No, don't stop tracking others
			[task startTracking];
			
			[self updateButton:myButton];
			myButton = nil;
			break;
	}
	
	NSError *error;
	if (![getManagedObjectContext() save:&error])
	{
		NSLog(@"Could not save efforts: %@", [error localizedDescription]);
		UIAlertView *alert = [[UIAlertView alloc] initWithTitle:@"Error" message:@"Error saving effort" delegate:self cancelButtonTitle:@"OK" otherButtonTitles:nil];
		[alert show];
		[alert release];
	}
}

#pragma mark Table view methods

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView
{
    return [[results sections] count] + 1;
}

- (CGFloat)tableView:(UITableView *)tableView heightForRowAtIndexPath:(NSIndexPath *)indexPath
{
	return (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPad) ? 40 : 44;
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section
{
	if (section == 0)
		return 1;

	return [[[results sections] objectAtIndex:section - 1] numberOfObjects];
}

- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath
{
	static NSString *CellIdentifier = @"Cell";
	
	UITableViewCell *cell = [tableView dequeueReusableCellWithIdentifier:CellIdentifier];
	if (cell == nil)
	{
		cell = [[[UITableViewCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:CellIdentifier] autorelease];
	}

	if (indexPath.section == 0)
	{
		cell.textLabel.text = [NSString stringWithFormat:_("Total spent: %@"), [NSString formatTimeInterval:totalSpent]];
	}
	else
	{
		CDEffort *effort = [results objectAtIndexPath:[NSIndexPath indexPathForRow:indexPath.row inSection:indexPath.section - 1]];
		
		if (effort.ended)
		{
			NSTimeInterval duration = [effort.ended timeIntervalSinceDate:effort.started];

			if (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPad)
			{
				cell.textLabel.text = [NSString stringWithFormat:_("From %@ to %@ (%@)"),
									   [[UserTimeUtils instance] stringFromDate:effort.started],
									   [[UserTimeUtils instance] stringFromDate:effort.ended],
									   [NSString formatTimeInterval:(NSInteger)duration]];
			}
			else
			{
				cell.textLabel.text = [NSString stringWithFormat:_("%@ on %@"), [NSString formatTimeInterval:(NSInteger)duration], [[UserTimeUtils instance] stringFromDate:effort.started]];
			}
		}
		else
		{
			cell.textLabel.text = [NSString stringWithFormat:_("Started %@"), [[UserTimeUtils instance] stringFromDate:effort.started]];
		}
	}
	
	cell.selectionStyle = UITableViewCellSelectionStyleNone;
	
	if (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPad)
	{
		cell.textLabel.font = [UIFont fontWithName:@"MarkerFelt-Thin" size:18];
	}
	
	return cell;
}

@end

