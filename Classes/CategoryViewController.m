//
//  CategoryViewController.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 14/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "NavigationController.h"
#import "CategoryViewController.h"
#import "StringChoiceController.h"
#import "TaskViewController.h"
#import "SyncViewController.h"

#import "Database/Database.h"
#import "Database/Statement.h"

#import "Domain/Category.h"

#import "Configuration.h"

@implementation CategoryViewController

@synthesize navigationController;
@synthesize syncButton;

- (void)willTerminate
{
	[[PositionStore instance] push:self indexPath:nil];
}

- (void)restorePosition:(Position *)pos store:(PositionStore *)store
{
	[self.tableView setContentOffset:pos.scrollPosition animated:NO];
	
	if (pos.indexPath)
	{
		[self.tableView selectRowAtIndexPath:pos.indexPath animated:NO scrollPosition:UITableViewScrollPositionNone];

		TaskViewController *ctrl;
		
		if (pos.indexPath.row)
		{
			ctrl = [[TaskViewController alloc] initWithTitle:[[categories objectAtIndex:pos.indexPath.row - 1] name] category:[[categories objectAtIndex:pos.indexPath.row - 1] objectId] categoryController:self];
		}
		else
		{
			ctrl = [[TaskViewController alloc] initWithTitle:NSLocalizedString(@"All", @"All categories view title") category:-1 categoryController:self];
		}
		
		[[PositionStore instance] push:self indexPath:pos.indexPath];
		
		[self.navigationController pushViewController:ctrl animated:YES];
		[ctrl release];

		[store restore:ctrl];
	}
}

- (void)viewDidLoad
{
	[super viewDidLoad];
	
	NSArray *cachesPaths = NSSearchPathForDirectoriesInDomains(NSCachesDirectory, NSUserDomainMask, YES);
	NSString *cachesDir = [cachesPaths objectAtIndex:0];
	
	NSFileManager *fileManager = [NSFileManager defaultManager];
	if (![fileManager fileExistsAtPath:cachesDir])
	{
		[fileManager createDirectoryAtPath:cachesDir attributes:nil];
	}
	
	NSString *path = [cachesDir stringByAppendingPathComponent:@"positions.store"];
	
	if ([fileManager fileExistsAtPath:path])
	{
		PositionStore *store = [[PositionStore alloc] initWithFile:[cachesDir stringByAppendingPathComponent:@"positions.store"]];
		[store restore:self];
		[store release];
	}
	
	[fileManager release];
}

- (void)viewDidUnload
{
	[navigationController release];
	[syncButton release];
}

- (void)childWasPopped
{
	NSIndexPath *indexPath = [self.tableView indexPathForSelectedRow];

	if (indexPath)
	{
		[[PositionStore instance] pop];
		
		[self.tableView reloadData];

		// XXXFIXME: reloadData is not enough to refresh the task count ?

		for (NSIndexPath *path in [self.tableView indexPathsForVisibleRows])
			[self.tableView deselectRowAtIndexPath:path animated:YES];

		// And the above code does not actually deselect the selected cell. Duh...
		[self.tableView deselectRowAtIndexPath:indexPath animated:YES];
	}
	
	if (wantSync)
	{
		wantSync = NO;
		[self onSynchronize:nil];
	}
}

- (void)setWantSync
{
	wantSync = YES;
}

- (IBAction)onAddCategory:(UIBarButtonItem *)button
{
	StringChoiceController *ctrl = [[StringChoiceController alloc] initWithPlaceholder:NSLocalizedString(@"Enter category name", @"New category placeholder") target:self action:@selector(onCategoryAdded:)];
	[self.navigationController presentModalViewController:ctrl animated:YES];
	[ctrl release];
}

- (void)onCategoryAdded:(NSString *)name
{
	if (name != nil)
	{
		Statement *req = [[Database connection] statementWithSQL:@"INSERT INTO Category (name) VALUES (?)"];
		[req bindString:name atIndex:1];
		[req exec];
		[self loadCategories];
		[self.tableView reloadData];
	}

	[self.navigationController dismissModalViewControllerAnimated:YES];
}

- (void)fillCell:(UITableViewCell *)cell forCategory:(Category *)category
{
	[super fillCell:cell forCategory:category];

#ifdef __IPHONE_3_0
	cell.textLabel.text = [NSString stringWithFormat:@"%@ (%d)", [category name], [category count]];
#else
	cell.text = [NSString stringWithFormat:@"%@ (%d)", [category name], [category count]];
#endif
}

#pragma mark Table view methods

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section
{
    return [super tableView:tableView numberOfRowsInSection:section] + 1;
}

- (void)tableView:(UITableView *)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath
{
	TaskViewController *ctrl;
	
	if (indexPath.row)
	{
		ctrl = [[TaskViewController alloc] initWithTitle:[[categories objectAtIndex:indexPath.row - 1] name] category:[[categories objectAtIndex:indexPath.row - 1] objectId] categoryController:self];
	}
	else
	{
		ctrl = [[TaskViewController alloc] initWithTitle:NSLocalizedString(@"All", @"All categories view title") category:-1 categoryController:self];
	}
	
	[[PositionStore instance] push:self indexPath:indexPath];
	
	[self.navigationController pushViewController:ctrl animated:YES];
	[ctrl release];
}

- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath
{
	UITableViewCell *cell;

	if (indexPath.row)
	{
		cell = [super tableView:tableView cellForRowAtIndexPath:[NSIndexPath indexPathForRow:indexPath.row - 1 inSection:indexPath.section]];
	}
	else
	{
		static NSString *CellIdentifier = @"Cell";
		
		cell = [tableView dequeueReusableCellWithIdentifier:CellIdentifier];
		if (cell == nil)
		{
			cell = [[[UITableViewCell alloc] initWithFrame:CGRectZero reuseIdentifier:CellIdentifier] autorelease];
		}

#ifdef __IPHONE_3_0
		cell.textLabel.text = NSLocalizedString(@"All", @"All categories name");
#else
		cell.text = NSLocalizedString(@"All", @"All categories name");
#endif
	}

	cell.accessoryType = UITableViewCellAccessoryDisclosureIndicator;
	return cell;
}

//===========================================================

- (IBAction)onSynchronize:(UIBarButtonItem *)button
{
	button.enabled = NO;

	if (![Configuration configuration].name)
	{
		// Name/domain not defined, browse
		BonjourBrowser *browser = [[BonjourBrowser alloc] initForType:@"_taskcoachsync._tcp" inDomain:@"local." customDomains:nil showDisclosureIndicators:NO showCancelButton:YES];
		browser.delegate = self;
		browser.searchingForServicesString = NSLocalizedString(@"Looking for Task Coach", @"Bonjour search string");
		[self.navigationController presentModalViewController:browser animated:YES];
		[browser release];
	}
	else
	{
		NSNetService *srv = [[NSNetService alloc] initWithDomain:[Configuration configuration].domain type:@"_taskcoachsync._tcp" name:[Configuration configuration].name];
		srv.delegate = self;
		[srv resolveWithTimeout:5];
	}
}

// NSNetService delegate

- (void)netService:(NSNetService *)sender didNotResolve:(NSDictionary *)errorDict
{
	// Browse again...

	BonjourBrowser *browser = [[BonjourBrowser alloc] initForType:@"_taskcoachsync._tcp" inDomain:@"local." customDomains:nil showDisclosureIndicators:NO showCancelButton:YES];
	browser.delegate = self;
	browser.searchingForServicesString = NSLocalizedString(@"Looking for Task Coach", @"Bonjour search string");
	[self.navigationController presentModalViewController:browser animated:YES];
	[browser release];
	[sender release];
}

- (void)netServiceDidResolveAddress:(NSNetService *)sender
{
	SyncViewController *ctrl = [[SyncViewController alloc] initWithTarget:self action:@selector(onSyncFinished) host:[sender hostName] port:[sender port]];
	[self.navigationController presentModalViewController:ctrl animated:YES];
	[ctrl release];
}

- (void)onSyncFinished
{
	[self loadCategories];
	[self.tableView reloadData];
	[self.navigationController dismissModalViewControllerAnimated:YES];
	syncButton.enabled = YES;
}

- (void)bonjourBrowser:(BonjourBrowser*)browser didResolveInstance:(NSNetService*)ref
{
	if (ref)
	{
		NSLog(@"Found Task Coach: %@:%d", [ref hostName], [ref port]);

		[Configuration configuration].domain = [ref domain];
		[Configuration configuration].name = [ref name];
		[[Configuration configuration] save];

		SyncViewController *ctrl = [[SyncViewController alloc] initWithTarget:self action:@selector(onSyncFinished) host:[ref hostName] port:[ref port]];
		[self.navigationController.modalViewController presentModalViewController:ctrl animated:YES];
		[ctrl release];
	}
	else
	{
		syncButton.enabled = YES;
		[self.navigationController dismissModalViewControllerAnimated:YES];
	}
}

@end

