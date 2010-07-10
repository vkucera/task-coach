//
//  FileChooser.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 25/12/09.
//  Copyright 2009 Jérôme Laheurte. All rights reserved.
//

#import "TaskCoachAppDelegate.h"
#import "FileChooser.h"
#import "CategoryViewController.h"
#import "Configuration.h"
#import "i18n.h"

#import "CDFile.h"
#import "CDDomainObject.h"
#import "CDDomainObject+Addons.h"

@implementation FileChooser

- initWithController:(CategoryViewController *)ctrl
{
	if ((self = [super initWithNibName:@"FileChooser" bundle:[NSBundle mainBundle]]))
	{
		catCtrl = ctrl;

		NSFetchRequest *request = [[NSFetchRequest alloc] init];
		[request setEntity:[NSEntityDescription entityForName:@"CDFile" inManagedObjectContext:getManagedObjectContext()]];
		NSSortDescriptor *sd = [[NSSortDescriptor alloc] initWithKey:@"name" ascending:YES];
		[request setSortDescriptors:[NSArray arrayWithObject:sd]];
		[sd release];

		resultsCtrl = [[NSFetchedResultsController alloc] initWithFetchRequest:request managedObjectContext:getManagedObjectContext() sectionNameKeyPath:nil cacheName:@"CDFileCache"];
		[request release];
		
		NSError *error;
		if (![resultsCtrl performFetch:&error])
		{
			UIAlertView *alert = [[UIAlertView alloc] initWithTitle:@"Error" message:@"Could not load files" delegate:self cancelButtonTitle:@"OK" otherButtonTitles:nil];
			[alert show];
			[alert release];
		}
	}
	
	return self;
}

- (void)viewDidLoad
{
	[super viewDidLoad];

	[self setEditing:YES];
}

- (void)dealloc
{
	// Hack: if we do that before the animation is finished, the first row is not actually updated...
	[catCtrl.tableView reloadRowsAtIndexPaths:[NSArray arrayWithObject:[NSIndexPath indexPathForRow:0 inSection:0]] withRowAnimation:UITableViewRowAnimationNone];
	[resultsCtrl release];

	[super dealloc];
}

#pragma mark Table view methods

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView
{
    return [[resultsCtrl sections] count];
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section
{
	return [[[resultsCtrl sections] objectAtIndex:section] numberOfObjects];
}

- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath
{
    static NSString *CellIdentifier = @"Cell";
    
    UITableViewCell *cell = [tableView dequeueReusableCellWithIdentifier:CellIdentifier];
    if (cell == nil)
	{
        cell = [[[UITableViewCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:CellIdentifier] autorelease];
    }

	CDFile *file = [resultsCtrl objectAtIndexPath:indexPath];
	cell.textLabel.text = file.name;
	if (file == [Configuration configuration].cdCurrentFile)
		cell.editingAccessoryType = UITableViewCellAccessoryCheckmark;
	else
		cell.editingAccessoryType = UITableViewCellAccessoryNone;

    return cell;
}

- (void)tableView:(UITableView *)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath
{
	[Configuration configuration].cdCurrentFile = [resultsCtrl objectAtIndexPath:indexPath];
	[[Configuration configuration] save];

	[self.tableView reloadData];
	
	[catCtrl loadCategories];
	[catCtrl.navigationController dismissModalViewControllerAnimated:YES];
}

- (void)tableView:(UITableView *)tableView commitEditingStyle:(UITableViewCellEditingStyle)editingStyle forRowAtIndexPath:(NSIndexPath *)indexPath
{
	if (editingStyle == UITableViewCellEditingStyleDelete)
	{
		CDFile *file = [resultsCtrl objectAtIndexPath:indexPath];

		NSFetchRequest *request = [[NSFetchRequest alloc] init];
		[request setEntity:[NSEntityDescription entityForName:@"DomainObject" inManagedObjectContext:getManagedObjectContext()]];
		[request setPredicate:[NSPredicate predicateWithFormat:@"file == %@", file]];
		NSError *error;
		NSArray *results = [getManagedObjectContext() executeFetchRequest:request error:&error];
		
		if (results)
		{
			for (CDDomainObject *object in results)
				[getManagedObjectContext() deleteObject:object];
			[getManagedObjectContext() deleteObject:file];

			NSError *error;
			if (![getManagedObjectContext() save:&error])
			{
				UIAlertView *alert = [[UIAlertView alloc] initWithTitle:@"Error" message:@"Could not save data" delegate:self cancelButtonTitle:@"OK" otherButtonTitles:nil];
				[alert show];
				[alert release];
			}
		}
		else
		{
			NSLog(@"Could not fetch objects: %@", [error localizedDescription]);
			assert(0);
		}

		[request setEntity:[NSEntityDescription entityForName:@"CDFile" inManagedObjectContext:getManagedObjectContext()]];
		[request setPredicate:[NSPredicate predicateWithFormat:@"TRUE"]];
		results = [getManagedObjectContext() executeFetchRequest:request error:&error];
		[request release];

		if (results)
		{
			if ([results count] <= 1)
			{
				if ([results count])
					[Configuration configuration].cdCurrentFile = [results objectAtIndex:0];
				else
					[Configuration configuration].cdCurrentFile = nil;
				
				[[Configuration configuration] save];
				
				[catCtrl loadCategories];
				[catCtrl.navigationController dismissModalViewControllerAnimated:YES];
			}
		}
		else
		{
			NSLog(@"Could not fetch files: %@", [error localizedDescription]);
			assert(0);
		}
	}
}

@end

