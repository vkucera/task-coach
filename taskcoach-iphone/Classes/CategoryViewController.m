//
//  CategoryViewController.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 14/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import "CategoryViewController.h"
#import "NavigationController.h"
#import "StringChoiceController.h"
#import "TaskViewController.h"
#import "SyncViewController.h"

#import "Database/Database.h"
#import "Database/Statement.h"

#import "Domain/Category.h"
#import "PositionStore.h"

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
			ctrl = [[TaskViewController alloc] initWithTitle:[[categories objectAtIndex:pos.indexPath.row - 1] name] category:[[categories objectAtIndex:pos.indexPath.row - 1] objectId]];
		}
		else
		{
			ctrl = [[TaskViewController alloc] initWithTitle:NSLocalizedString(@"All", @"All categories view title") category:-1];
		}
		
		[[PositionStore instance] push:self indexPath:pos.indexPath];
		
		[self.navigationController pushViewController:ctrl animated:YES];
		[ctrl release];

		[store restore:ctrl];
	}
}

- (void)addCategory:(NSDictionary *)dict
{
	Category *category = [[Category alloc] initWithId:[[dict objectForKey:@"id"] intValue] name:[dict objectForKey:@"name"]
											   status:[[dict objectForKey:@"status"] intValue] taskCoachId:[dict objectForKey:@"taskCoachId"]
											   parentId:[dict objectForKey:@"parentTaskCoachId"]];
	[categories addObject:category];
}

- (void)loadCategories
{
	[categories removeAllObjects];

	// We're assuming that there are not a bunch of categories, therefore we keep them in memory.
	// This is not the case with tasks.
	
	Statement *req = [[Database connection] statementWithSQL:@"SELECT * FROM Category WHERE status != 3 ORDER BY name"];
	[req execWithTarget:self action:@selector(addCategory:)];

	NSMutableDictionary *dict = [[NSMutableDictionary alloc] initWithCapacity:8];
	NSMutableArray *rootItems = [[NSMutableArray alloc] initWithCapacity:8];

	for (Category *category in categories)
	{
		if (category.taskCoachId)
		{
			[dict setObject:category forKey:category.taskCoachId];
			if (!category.parentId)
				[rootItems addObject:category];
		}
		else
		{
			[rootItems addObject:category];
		}
	}

	for (Category *category in categories)
	{
		if (category.parentId)
		{
			Category *parent = [dict objectForKey:category.parentId];
			[parent addChild:category];
		}
	}

	[categories removeAllObjects];
	for (Category *category in rootItems)
	{
		[category finalizeChildren:categories];
	}

	[dict release];
	[rootItems release];
}

- (void)viewDidLoad
{
	categories = [[NSMutableArray alloc] init];
	[self loadCategories];

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

- (void)childWasPopped
{
	NSIndexPath *indexPath = [self.tableView indexPathForSelectedRow];
	
	if (indexPath)
	{
		[[PositionStore instance] pop];
		
		if (indexPath.row)
		{
			[self.tableView reloadData];
		}

		// XXXFIXME: because of the reloadData, this isn't actually animated, but it is needed
		// to refresh the task count...

		[self.tableView deselectRowAtIndexPath:indexPath animated:YES];
	}
}

- (void)dealloc
{
	[categories release];

    [super dealloc];
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

#pragma mark Table view methods

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView
{
    return 1;
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section
{
    return [categories count] + 1;
}

- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath
{
    static NSString *CellIdentifier = @"Cell";

    UITableViewCell *cell = [tableView dequeueReusableCellWithIdentifier:CellIdentifier];
    if (cell == nil)
	{
        cell = [[[UITableViewCell alloc] initWithFrame:CGRectZero reuseIdentifier:CellIdentifier] autorelease];
		cell.accessoryType = UITableViewCellAccessoryDisclosureIndicator;
    }
    
	if (indexPath.row)
	{
		Category *category = [categories objectAtIndex:indexPath.row - 1];

#ifdef __IPHONE_3_0
		cell.textLabel.text = [NSString stringWithFormat:@"%@ (%d)", [category name], [category count]];
#else
		cell.text = [NSString stringWithFormat:@"%@ (%d)", [category name], [category count]];
#endif
		cell.indentationLevel = category.level;
	}
	else
	{
#ifdef __IPHONE_3_0
		cell.textLabel.text = NSLocalizedString(@"All", @"All categories name");
#else
		cell.text = NSLocalizedString(@"All", @"All categories name");
#endif
	}

    return cell;
}

- (void)tableView:(UITableView *)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath
{
	TaskViewController *ctrl;
	
	if (indexPath.row)
	{
		ctrl = [[TaskViewController alloc] initWithTitle:[[categories objectAtIndex:indexPath.row - 1] name] category:[[categories objectAtIndex:indexPath.row - 1] objectId]];
	}
	else
	{
		ctrl = [[TaskViewController alloc] initWithTitle:NSLocalizedString(@"All", @"All categories view title") category:-1];
	}
	
	[[PositionStore instance] push:self indexPath:indexPath];
	
	[self.navigationController pushViewController:ctrl animated:YES];
	[ctrl release];
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

