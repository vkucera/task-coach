//
//  AuthentificationState.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 24/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "KeychainWrapper.h"
#import "OneShotItemState.h"

@interface AuthentificationState : OneShotItemState <UITextFieldDelegate>
{
	NSInteger state;
	NSMutableDictionary *currentPasswords;
	NSData *currentData;
	
#if !TARGET_IPHONE_SIMULATOR
	KeychainWrapper *keychain;
#endif
}

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller;

@end
