<?php
/**********************************************************************
 *
 * $Id: auth.php,v 1.1 2006/07/05 15:19:26 dmorissette Exp $
 *
 * purpose: Implementation of authentication and access control
 *
 * author: Daniel Morissette (dmorissette@mapgears.com)
 *
 **********************************************************************
 *
 * Copyright (c) 2005, DM Solutions Group Inc.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a
 * copy of this software and associated documentation files (the "Software"),
 * to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense,
 * and/or sell copies of the Software, and to permit persons to whom the
 * Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included
 * in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
 * THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
 * DEALINGS IN THE SOFTWARE.
 *
 **********************************************************************/

/*
 * This file provides a simple authentication and access control scheme
 * to allow controlling access to layers and application features by user.
 * It should be possible to write a drop-in replacement for this file to 
 * different access control mechanisms.
 * 
 * This implementation uses the $_SERVER['REMOTE_USER'] variable to lookup 
 * the authenticated visitor name. This implies that user/password validation
 * is handled by Apache using Basic Authentication (.htaccess + htpasswd 
 * files).
 *
 * If $_SERVER['REMOTE_USER'] is not set then access control is disabled,
 * or in other words everything is wide open.
 *
 * AuthorizedUsers array:
 * ----------------------
 *
 * The kaBasicAuthentication() constructor takes an AuthorizedUsers array
 * as argument that contains a list of privileges and for each privilege
 * the list of user ids that are authorized to access this named privilege.
 * The privilege name can be either a map layer/group name, or an application
 * feature.
 *
 * e.g. array( 'layer1' => array('user1', 'user2', 'user3'),
 *             'layer2' => array('user1', 'user2'),
 *             'tool.identify' => array('user1') )
 *
 * If no entry is set for a given privilege in the AuthorizedUsers array then
 * this privilege is available to all (i.e. testPrivilege() will always return
 * TRUE for this privilege).
 *
 */


class kaBasicAuthentication
{
    var $bAuthEnabled;
    var $szRemoteUser;
    var $aAuthorizedUsers;

    /* Constructor
     */
    function kaBasicAuthentication($aAuthUsers)
    {
        /* Remote user id used for authentication.
         * By default it's in REMOTE_USER, except with PHP as a CGI where it's
         * in REDIRECT_REMOTE_USER 
         */
        if (isset($_SERVER['REMOTE_USER']))
            $this->szRemoteUser = $_SERVER['REMOTE_USER'];
        else
            $this->szRemoteUser = $_SERVER['REDIRECT_REMOTE_USER'];

        /* Read $szAuthConfigFile if it exists
         */
        $this->aAuthorizedUsers = $aAuthUsers;

        /* Flag to indicate whether authentication is enabled or not, to
         * quickly return from all methods and save CPU cycles when it's
         * disabled
         */
        $this->bAuthEnabled = ( isset($this->szRemoteUser) && 
                                isset($this->aAuthorizedUsers) );
    }


    /* function testPrivilege()
     *
     * Check that user has the specified privilege. Privilege name can be
     * a layer/group name or an application feature. Returns TRUE/FALSE.
     * 
     * Layers/privileges without an entry in the $aAuthorizedUsers" array 
     * are accessible to all.
     */
    function testPrivilege($szPrivName)
    {
        if (!$this->bAuthEnabled)
            return TRUE;  /* All privs available when auth. is not enabled */

        if (isset($this->aAuthorizedUsers[$szPrivName]) &&
            in_array($this->szRemoteUser, 
                     $this->aAuthorizedUsers[$szPrivName]) == FALSE)
        {
            /* User is not authorized. */
            return FALSE;
        }
        
        return TRUE;
    }

}

